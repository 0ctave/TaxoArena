"""hier_fair_backoff.py: HIER-FAIR-BACKOFF (HB1, HB2 deciding on TRAIN-CV; HB3 scored secondary on EVAL, descriptive by Support) and
BACKOFF-ROBUST (R1: the HB1 / HB2 words under TAU200 and under NO-XSRC) -- does AF-U's back-off routing beat back-off over a
SHAPE-MATCHED spherical k-means hierarchy (AF-U's per-level node counts, AF-U's filing rule), and is the tree's back-off gain over its
own flat leaves larger than the k-means hierarchy's? ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A
CPU reader of keyed correctness; a POOL READER (rule 7).

REGISTRATIONS OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — HIER-FAIR-BACKOFF: under TRAIN cross-validation by
  CK-CLOSE component on the content-closed v2 union split, does AF-U's back-off routing beat back-off over a SHAPE-MATCHED spherical
  k-means hierarchy ..." (L24974-L24987, written at e83b59d5, parent d8ab39fa): HB1, HB2, HB3, LIKE WITH LIKE, Support (a)-(g),
  P1-P6, F-HB, WILL NOT SHOW.
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — BACKOFF-ROBUST: do HIER-FAIR-BACKOFF's words survive
  (i) one fixed shrinkage strength tau = 200 for every arm and (ii) removal of the items AF-U files into another source's leaf?"
  (L24989-L25000, same commit): R1, Support (a)-(g), P1-P3, F-BR. Record: "## Registrar's record 2026-10-08 ... six zero-call tests
  registered ..." (L24950).
  PILOT DISCLOSURE (registered; SEEN, pilot role only, never evidence): E:/TaxoArena_tmp/hier_tests/test3_fair_backoff (fair_backoff.py;
  results.json sha256 866284ca1bb5cf98...; review/verify.json 97e9815d9f5677e4...), and E:/TaxoArena_tmp/cert_split,
  E:/TaxoArena_tmp/hier_tests/granularity_free and nesting, E:/TaxoArena_tmp/scpb/review_v3_synthesis.md. The deciding legs RE-READ
  the pilot's 11,841 TRAIN items (fresh folds, the GATE tau rule): a registered confirmation, NOT an independent replication.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, or with --data-root <main checkout>; rule 7: every mode below except
--selftest / --mutants is a POOL READER: `powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` first, exit 1 = free):
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/hier_fair_backoff.py --selftest   # fixtures; no DB of record
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/hier_fair_backoff.py --mutants    # the mutant table
  1. python tools/analysis/hier_fair_backoff.py --dry-run   # POOL line first; pins; denominators; the B0-2 pool check; the UNION-AF-
                     # ROUTE inputs re-hashed; frozen policy sha; AF-U hierarchy; the five shape-matched k-means hierarchies built and
                     # their per-level node counts checked against AF-U's; NO key (TRAIN, GATE or EVAL), NO statistic; writes nothing
  2. python tools/analysis/hier_fair_backoff.py --run       # TRAIN key; GATE key (tau only); TRAIN-CV computed BEFORE the eval view
                     # opens; ONE EVAL key read (marker first; HB3); outcome WRITE-ONCE:
       experiment_results/archv2/hier_fair_backoff/outcome.txt (+ hier_fair_backoff.READ_STARTED). Never committed: pin by sha256
       and back up to E:/TaxoArena_backup_<date>_hier_fair_backoff with SHA256SUMS.txt.
  Expected CPU (one thread): five shape-matched hierarchies (spherical k-means within ~110 AF-U nodes on <= 11.8k x 256 rows, seconds
  each); TRAIN-CV 10 folds x 11 arms x 11 taus back-off fits (~1 min); the CV bootstrap B 2,000 (~1 min); HB3: tree_backoff's
  run_boot with an 11-arm back-off hook, B 2,000 (TREE-BACKOFF's run took minutes): about 10-30 min in all.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome and marker absent (write-once); denominators; (2) union_route_common.prepare (B0-2 pool check, AF-U state,
  inputs manifest sha256-lf 53021e26... with every file re-hashed, AF and K0..K4 cells, the frozen TRAIN policy 8d68018c...); the
  AF-U hierarchy (tree_backoff.af_hier, unchanged); the bundle's TRAIN rows; per seed s the shape-matched hierarchy BC_s ([HFB-SHAPE]
  refuses unless its per-level node counts equal AF-U's); every routed / GATE item's vector (escalation_rc.get_vectors, equal to the
  bundle's); (3) the gen view's TRAIN key; between it and the eval view: the GATE key (escalation_curve.gate_key), [HFB-GATE-DENOM]
  1,944, [HFB-GATE-SIDE], the TRAIN-CV scored set ([HFB-CV-DENOM] 11,841 items / 10,781 components), the folds, every fold's
  policies and GATE tau*, the CV bootstrap: HB1, HB2 and R1 are FIXED before the eval view opens; (4) the eval view, the marker,
  THE EVAL KEY READ; [HFB-DENOM] 5,907 / 5,404; [B3]; (5) HB3: tau* per arm on GATE (full-TRAIN fits), tree_backoff's run_boot hook
  (B 2,000, default_rng(42)) with TF, TB, BCF_s, BCB_s; the IDENTITY precondition (UNION-AF-ROUTE's digits) before any new number is
  printed; [HFB-MIRROR] (the hook's TF / BEST equal run_boot's TREE / best single); (6) every line; the outcome written mode "x".

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  HB-R1 SHAPE-MATCHED HIERARCHY BC_s: per source in the registered order, starting at the source's AF-U root with the source's bundle
        TRAIN rows (bundle class -> source); at every AF-U node v with c_v children, the node's rows are split by spherical k-means
        into c_v clusters (g13_breakdown.ukm_fit: k-means++ then Lloyd, seed s; c_v = 1 keeps every row; a node with no more rows
        than children gives one row per cluster and empties: counted, printed); clusters ordered by size (desc, ties by index) are
        matched to v's children ordered by (leaf count desc, AF-U TRAIN items under desc, name) and the recursion continues with the
        matched child's subtree, so BC_s copies AF-U's topology exactly; a one-cell source keeps one cell (its rows' mean); the
        union root and the pseudo-leaves as AF-U's. Leaf centroid = the normalised mean of its rows (an empty leaf has none and is
        never filed to). Per-level node counts (pseudo-leaves excluded) must equal AF-U's per seed ([HFB-SHAPE]).
  HB-R2 FILING (the same rule as AF-U's flatLeaf): an item goes to the BC_s leaf whose centroid has the largest cosine with its 256-d
        vector, over ALL leaves (no source gating; numpy argmax = the first leaf on a tie). An item whose AF-U cell is a pseudo-leaf
        ("<no-routing-row>", "<unrouted>") keeps that pseudo-leaf in every arm. AF-U's own cells are union_af_route's af_cells.
  HB-R3 TRAIN-CV SCORED SET: the gen view's key-complete TRAIN items with an AF-U filing leaf (not a pseudo-leaf) and a vector
        (the pilot's set): 11,841 / 10,781 or [HFB-CV-DENOM]. FOLDS: fold = int(sha256(component id + "HIER-FAIR-BACKOFF-FOLDS-1"),
        hex) mod 10. Per fold f: every node statistic of every arm on the items of the other nine folds (tree_backoff.node_stats,
        unit weights), the picks tree_backoff.picks (tau = 0 IS the flat policy: argmax, a leaf with TRAIN mass < 1 -> the best
        single); tau* per arm and seed and fold = the first maximum of the number of correct GATE picks over the registered grid
        (ties to the smaller tau); the fold's items scored once by TF / TB (tau*) / TB200 (tau 200) and BCF_s / BCB_s / BCB200_s.
        KWF_s (descriptive) = the K_s cells of record (k_cells_s<s>.tsv: per-source spherical k-means at AF-U's per-source leaf
        counts, 123 cells, [SC]) at tau 0.
  HB-R4 D_final = acc(TB) - mean_s acc(BCB_s); D_gain = [acc(TB) - acc(TF)] - mean_s [acc(BCB_s) - acc(BCF_s)] (item-paired, pp in
        print). INTERVAL: two-stage bootstrap, B 2,000, default_rng(20261008); per replicate the C CK-CLOSE components are drawn with
        replacement (rng.integers(0, C, C)), THEN the five seeds (rng.integers(0, 5, 5)); every column's accuracy = sum over drawn
        components / their item count; the seed mean over the drawn seeds; 95% = percentiles 2.5 / 97.5, 90% = 5 / 95 (numpy,
        linear); SE = the replicate SD. DEFF (Support (b), printed beside) = Var(two-stage) / Var(component-only: the same component
        draws, all five seeds); n_eff = components / DEFF; MDE80 = 2.8 SE. Every subset and leg uses the SAME replicate draws.
  HB-R5 HB1: TREE-BETTER iff the 95% lower bound > 0; else KMEANS-BETTER iff the 95% upper bound < 0; else PARITY iff the 90%
        interval lies inside [-0.60, +0.60]pp (closed: lo90 >= -0.0060 and hi90 <= +0.0060); else NEITHER. HB2: DIVIDEND-TREE iff
        lo95 > 0; DIVIDEND-KMEANS iff hi95 < 0; NEITHER otherwise. Rule 8: PARITY refuted iff the word is not PARITY (a sign word or
        a 90% interval leaving +/-0.60pp); TREE-BETTER refuted iff lo95 <= 0; DIVIDEND-TREE refuted iff lo95 <= 0. F-HB iff HB1 =
        KMEANS-BETTER.
  HB-R6 BACKOFF-ROBUST: TAU200 = TB200 / BCB200 (tau 200 in every fold and seed); NO-XSRC = the same CV picks scored on the items
        whose AF-U leaf's member (union_cells_io.cell_member) equals their stratum source (tree_backoff R8's rule); the count per
        fold printed. R1: ROBUST iff both legs' (HB1, HB2) words equal the reference words; FRAGILE-TAU iff only TAU200's differ;
        FRAGILE-XSRC iff only NO-XSRC's differ; FRAGILE-BOTH iff both. F-BR iff FRAGILE-XSRC or FRAGILE-BOTH.
  HB-R7 HB3 (EVAL; DESCRIPTIVE-ONLY by Support): TRAIN-fitted policies (full TRAIN of G14's reader, pseudo-leaf items included as in
        TREE-BACKOFF), tau* per arm on GATE (tree_backoff.choose_tau), tree_backoff's hook in v2_declared_cells.run_boot (TRAIN units
        resampled and every node re-fitted, EVAL components within stratum; B 2,000, default_rng(42)); D = point +- 1.96 SE_2stage
        (union_route_common.interval); sign words TREE-BETTER (lo > 0) / KMEANS-BETTER (hi < 0) / NEITHER, and HB2's words; NO_XSRC
        (the 191 of R-KI1) printed beside.
  HB-R8 Predictions "X [lo, hi]" HELD iff lo <= X <= hi; outcome probabilities by the multi-outcome Brier sum (an unlisted outcome has
        probability 0); a binary probability by (p - event)^2.
  NOT APPLICABLE (stated): no judge verdict (keyed correctness): no wrong(established) count, no tie convention A / B; no call cache,
        --pilot or truncation guard (zero calls).

SELFTEST / MUTANTS: see selftest() (every deciding path EXECUTED: --run end to end on tree_backoff's deepened union fixture against an
independent loop oracle, the CV core on planted data, the words and every printed branch, refusals, --dry-run) and MUTANTS (the
table with results is in the commit message).
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import json          # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
from types import SimpleNamespace   # noqa: E402
from collections import Counter     # noqa: E402

import numpy as np   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


TB_PIN = ("tree_backoff.py", "da80c57e927c6ebf8a1db9e2f0420c96c1514519")
if _blob_lf(os.path.join(HERE, TB_PIN[0])) != TB_PIN[1]:
    raise SystemExit("[HFB] REFUSED: tree_backoff.py is blob:%s, not the pinned blob:%s" % (_blob_lf(os.path.join(HERE, TB_PIN[0])), TB_PIN[1]))
import tree_backoff as TB    # noqa: E402  (pins union_route_common, union_cells_io, union_af_route, v2_declared_cells, escalation_curve)

U, EC = TB.U, TB.EC
ERC, UAR, V, GB, GC, UCI, FM = TB.ERC, TB.UAR, TB.V, TB.GB, TB.GC, TB.UCI, TB.FM

TAG = "[HFB]"
TEST_ID = "HIER-FAIR-BACKOFF"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — HIER-FAIR-BACKOFF: under TRAIN cross-'
            'validation by CK-CLOSE component on the content-closed v2 union split, ..." L24974-L24987 and "... — BACKOFF-ROBUST: ..."'
            ' L24989-L25000 (written at e83b59d5, parent d8ab39fa)')
OUT = "experiment_results/archv2/hier_fair_backoff"
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/hier_fair_backoff.READ_STARTED", n_gate_key=1944, n_cv=11841,
           comp_cv=10781, taus=TB.TAUS, nfold=10, fold_salt="HIER-FAIR-BACKOFF-FOLDS-1", B_cv=2000, cv_seed=20261008,
           kseeds=(0, 1, 2, 3, 4), parity=0.0060, tau_fixed=200, n_xsrc_eval=191)
FIXTURE_REG = dict(out="res/hfb/outcome.txt", marker="res/hfb/READ_STARTED")
_REG = [REG]


def reg():
    return _REG[0]


UNION = TB.UNION
PSEUDO = TB.PSEUDO
HIT = Counter()
SEEDS = (0, 1, 2, 3, 4)
SUPPORT = dict(deff_final=1.61, deff_gain=1.56, n_eff_final=6696, n_eff_gain=6911, se_final=0.00195, se_gain=0.00220,
               mde_final=0.0055, mde_gain=0.0062, tost_need=0.00485, hb3_se=0.00441, hb3_mde=0.0123,
               se_tau=0.00147, mde_tau=0.0041, se_xsrc=0.00198, mde_xsrc=0.0055)
VERDICT_HB = ("(f) VERDICT LINE (registered): HB1's sign words DESCRIPTIVE-ONLY (predicted |D_final| 0.05pp < MDE80 0.55pp); HB1 PARITY"
              " SCOREABLE (0.55 > 0.485); HB2 DESCRIPTIVE-ONLY (predicted +0.50pp, 0.12 short of 0.62pp); HB3 DESCRIPTIVE-ONLY (MDE80 1.23pp)")
VERDICT_BR = ("(f) VERDICT LINE (registered): under TAU200 KMEANS-BETTER is SCOREABLE (narrowly; predicted -0.45pp beyond MDE80 0.41pp),"
              " so FRAGILE-TAU vs not is SCOREABLE; under NO-XSRC DESCRIPTIVE-ONLY (a word change there would be noise-level)")
PILOT_SEEN = ("PILOT DISCLOSURE (registered): the 2026-10-07 exploratory numbers were SEEN (pilot role only, never evidence):"
              " E:/TaxoArena_tmp/hier_tests/test3_fair_backoff (results.json sha256 866284ca1bb5cf98..., review/verify.json"
              " 97e9815d9f5677e4...), E:/TaxoArena_tmp/cert_split, hier_tests/granularity_free and nesting, E:/TaxoArena_tmp/scpb/"
              "review_v3_synthesis.md; the deciding legs re-read the pilot's TRAIN items: NOT an independent replication")
PRED = dict(P1=(-0.0040, 0.0030), P2=(("PARITY", 0.70), ("NEITHER", 0.20), ("KMEANS-BETTER", 0.07), ("TREE-BETTER", 0.03)),
            P3=(0.0010, 0.0090), P4=(("DIVIDEND-TREE", 0.80), ("NEITHER", 0.20), ("DIVIDEND-KMEANS", 0.00)), P5=(-0.0130, 0.0070),
            P6=(50, 200))
PRED_BR = dict(P1=(-0.0080, -0.0010), P1W=(("KMEANS-BETTER", 0.60), ("NEITHER", 0.30), ("PARITY", 0.10), ("TREE-BETTER", 0.0)),
               P2=(-0.0045, 0.0030), P2EQ=0.80,
               P3=(("FRAGILE-TAU", 0.55), ("ROBUST", 0.30), ("FRAGILE-BOTH", 0.10), ("FRAGILE-XSRC", 0.05)))
FHB_FIRES = ("FALSIFIER F-HB: FIRES (HB1 KMEANS-BETTER): back-off over a shape-matched k-means hierarchy routes better than back-off"
             " over the tree; TREE-BACKOFF's HIERARCHY-HELPS is a property of any hierarchy of that shape, beaten by k-means content;"
             " every 'the tree's hierarchy routes better' sentence is withdrawn")
FBR_FIRES = ("FALSIFIER F-BR: FIRES (R1 %s): HIER-FAIR-BACKOFF's words depend on AF-U's cross-source filings; they are quoted only"
             " with the filing qualifier (UNION-AF-ROUTE D-4)")
WNS = ("WILL NOT SHOW (registered): an independent replication (the deciding leg re-reads the pilot's items); a label-free result"
       " (every arm [SC]); judged decisions; other rosters, draws, embedders or splits; equality under PARITY (parity within +/-0.60pp,"
       " never 'equal'); a gain outside MMLU_PRO if MMLU_PRO carries it; any sub-anchor profile")
WNS_BR = ("WILL NOT SHOW (registered, BACKOFF-ROBUST): that any tau is right (tau 200 is a perturbation, not a recommendation); a"
          " filing-free comparison (NO-XSRC is a subset, [SC]); an independent replication; EVAL claims (HB3's legs descriptive)")


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


# ── the shape-matched hierarchy (HB-R1, HB-R2) ──────────────────────────────────────────────────────────────────────────
def level_counts(h):
    real = ~h.pseudo
    return [int(((h.depth == d) & real).sum()) for d in range(1, int(h.depth.max()) + 1)]


def children_of(h):
    ch = {v: [] for v in range(h.N)}
    for v in range(h.N):
        if h.parent[v] >= 0:
            ch[int(h.parent[v])].append(v)
    return ch


def bc_build(H, Xt, tsrc, sources, single, seed, af_under, kfit=None):
    """HB-R1: the shape-matched spherical k-means hierarchy of seed s -> (Hier, leaf centroids (L, d), centroid leaf names, info)."""
    kfit = kfit or (lambda X, k, s: np.asarray(GB.ukm_fit(X, k, s)[0]["labels"], dtype=np.int64))
    ch = children_of(H)
    lc = {}

    def leafcount(v):
        if v not in lc:
            lc[v] = 1 if not ch[v] else sum(leafcount(c) for c in ch[v])
        return lc[v]
    root_of = {}
    for c in ch[H.root]:
        nm = H.names[c]
        if nm in PSEUDO:
            continue
        so = nm.split(":", 1)[0]                     # AF-U cell naming = the bundle's source naming (no view alias)
        if so not in single:
            if so in root_of:
                refuse("[HFB-SHAPE] source %s has two AF-U roots" % so)
            root_of[so] = c
    tag = "BC%d|" % seed
    names, parents, leaves, cents, cnames = [UNION], [None], set(), [], []
    degenerate, empty = 0, 0
    for so in sources:
        rows = np.flatnonzero(np.asarray(tsrc) == so)
        if so in single:
            nm = tag + single[so]["cell"]
            names.append(nm)
            parents.append(UNION)
            leaves.add(nm)
            if len(rows):
                cents.append(FM.unit_rows(Xt[rows].sum(axis=0, keepdims=True))[0])
                cnames.append(nm)
            else:
                empty += 1
            continue
        if so not in root_of:
            refuse("[HFB-SHAPE] source %s has no AF-U root" % so)
        stack = [(root_of[so], rows, UNION)]
        while stack:
            v, idx, par = stack.pop()
            nm = tag + H.names[v]
            names.append(nm)
            parents.append(par)
            kids = ch[v]
            if not kids:
                leaves.add(nm)
                if len(idx):
                    cents.append(FM.unit_rows(Xt[idx].sum(axis=0, keepdims=True))[0])
                    cnames.append(nm)
                else:
                    empty += 1
                continue
            bk = len(kids)
            if bk == 1:
                lab = np.zeros(len(idx), dtype=np.int64)
            elif len(idx) > bk:
                lab = kfit(Xt[idx], bk, seed)
            else:
                lab = np.arange(len(idx), dtype=np.int64)
                degenerate += 1
            clus = sorted(range(bk), key=lambda j: (-int((lab == j).sum()), j))
            ko = sorted(kids, key=lambda c: (-leafcount(c), -int(af_under[c]), H.names[c]))
            for c, j in zip(ko, clus):
                stack.append((c, idx[lab == j], nm))
    for p in PSEUDO:
        names.append(p)
        parents.append(UNION)
        leaves.add(p)
    h = TB.Hier("BC%d" % seed, names, parents, leaves)
    return h, (np.vstack(cents) if cents else np.zeros((0, Xt.shape[1]))), cnames, dict(degenerate=degenerate, empty=empty)


def check_shape(h_af, h_bc, label):
    a, b = level_counts(h_af), level_counts(h_bc)
    if a != b:
        hit("REFUSE.SHAPE")
        refuse("[HFB-SHAPE] %s per-level node counts %s differ from AF-U's %s" % (label, b, a))
    return a


def filer(C, cnames):
    """HB-R2: the nearest leaf centroid over ALL leaves (cosine; numpy argmax = the first leaf on a tie)."""
    Cn = FM.unit_rows(np.asarray(C, dtype=np.float64))
    return lambda x: cnames[int(np.argmax(Cn @ np.asarray(x, dtype=np.float64)))]


def flat_hier(label, cells):
    names = [UNION] + sorted(set(cells)) + [p for p in PSEUDO if p not in set(cells)]
    return TB.Hier(label, names, [None] + [UNION] * (len(names) - 1), set(names[1:]))


def fold_of(comp, salt, nfold):
    return int(hashlib.sha256((str(comp) + salt).encode("utf-8")).hexdigest(), 16) % nfold


# ── the TRAIN-CV core (HB-R3, HB-R4, HB-R6) ──────────────────────────────────────────────────────────────────────────────
def cv_predict(A, fold, arms, kw_arms, Kg, taus, nfold, tau_fixed):
    """Every fold's policies on the other nine; tau* per arm on GATE; the fold scored once -> (cols, tau*, per-fold info)."""
    n, m = A.shape
    D = SimpleNamespace(A=A, is_eval=np.zeros(n, dtype=bool), models=list(range(m)))
    cols = {}
    for a in arms:
        for leg in ("F", "B", "B200"):
            cols[(a, leg)] = np.full(n, np.nan)
    for a in kw_arms:
        cols[(a, "F")] = np.full(n, np.nan)
    cols[("BEST", "F")] = np.full(n, np.nan)
    tstar = {a: [] for a in arms}
    for f in range(nfold):
        ho = np.flatnonzero(fold == f)
        if not len(ho):
            for a in arms:
                tstar[a].append(None)
            continue
        w = (fold != f).astype(np.int64)
        gbs = set()
        for a, arm in arms.items():
            S, nn = TB.node_stats(D, arm, w)
            r = np.arange(len(arm.gate))
            counts = [int(Kg[r, TB.picks(arm.h, S, nn, t)[0][arm.gate]].sum()) for t in taus]
            ts = taus[int(np.argmax(counts))]
            tstar[a].append(ts)
            p0, gb = TB.picks(arm.h, S, nn, 0)
            pt, _g = TB.picks(arm.h, S, nn, ts)
            p2, _g = TB.picks(arm.h, S, nn, tau_fixed)
            gbs.add(gb)
            cols[(a, "F")][ho] = A[ho, p0[arm.pos[ho]]]
            cols[(a, "B")][ho] = A[ho, pt[arm.pos[ho]]]
            cols[(a, "B200")][ho] = A[ho, p2[arm.pos[ho]]]
        for a, arm in kw_arms.items():
            S, nn = TB.node_stats(D, arm, w)
            p0, gb = TB.picks(arm.h, S, nn, 0)
            gbs.add(gb)
            cols[(a, "F")][ho] = A[ho, p0[arm.pos[ho]]]
        if len(gbs) != 1:
            refuse("[HFB-MIRROR] fold %d: the arms disagree on the best single %s" % (f, sorted(gbs)))
        cols[("BEST", "F")][ho] = A[ho, gbs.pop()]
    for k, v in cols.items():
        if np.isnan(v).any():
            refuse("[HFB-CV] column %s has %d unscored item(s)" % (str(k), int(np.isnan(v).sum())))
    return cols, tstar


def cv_boot(cols, comp, masks, B, seed, nseeds, tree="AF", bc="BC"):
    """HB-R4: point and two-stage replicates of D_final and D_gain for every subset and leg; the component-only replicates (DEFF)."""
    uc, cidx = np.unique(np.asarray(comp), return_inverse=True)
    C = len(uc)
    keys = list(cols)
    M = np.vstack([cols[k] for k in keys]).T
    ix = {k: j for j, k in enumerate(keys)}
    out = {}
    sums = {}
    for nm, mk in masks:
        Sm = np.zeros((C, len(keys)))
        Nm = np.zeros(C)
        np.add.at(Sm, cidx[mk], M[mk])
        np.add.at(Nm, cidx[mk], 1.0)
        sums[nm] = (Sm, Nm, int(mk.sum()), len(np.unique(cidx[mk])))
    rng = np.random.default_rng(seed)
    reps = {nm: {leg: dict(final=np.empty(B), gain=np.empty(B), final_c=np.empty(B), gain_c=np.empty(B)) for leg in ("REF", "TAU200")}
            for nm, _mk in masks}
    seeds = list(range(nseeds))
    for b in range(B):
        cnt = np.bincount(rng.integers(0, C, C), minlength=C).astype(np.float64)
        sd = rng.integers(0, nseeds, nseeds)
        for nm, (Sm, Nm, _n, _c) in sums.items():
            acc = (cnt @ Sm) / (cnt @ Nm)
            for leg, lb in (("REF", "B"), ("TAU200", "B200")):
                t_b, t_f = acc[ix[(tree, lb)]], acc[ix[(tree, "F")]]
                k_b = np.array([acc[ix[("%s%d" % (bc, s), lb)]] for s in seeds])
                k_f = np.array([acc[ix[("%s%d" % (bc, s), "F")]] for s in seeds])
                r = reps[nm][leg]
                r["final"][b] = t_b - k_b[sd].mean()
                r["gain"][b] = (t_b - t_f) - (k_b[sd] - k_f[sd]).mean()
                r["final_c"][b] = t_b - k_b.mean()
                r["gain_c"][b] = (t_b - t_f) - (k_b - k_f).mean()
    for nm, mk in masks:
        acc = M[mk].mean(axis=0) if mk.any() else np.full(len(keys), np.nan)
        o = dict(n=sums[nm][2], comp=sums[nm][3], acc={k: float(acc[ix[k]]) for k in keys})
        for leg, lb in (("REF", "B"), ("TAU200", "B200")):
            t_b, t_f = acc[ix[(tree, lb)]], acc[ix[(tree, "F")]]
            k_b = np.array([acc[ix[("%s%d" % (bc, s), lb)]] for s in seeds])
            k_f = np.array([acc[ix[("%s%d" % (bc, s), "F")]] for s in seeds])
            r = reps[nm][leg]
            o[leg] = dict(final=interval(float(t_b - k_b.mean()), r["final"], r["final_c"], o["comp"]),
                          gain=interval(float((t_b - t_f) - (k_b - k_f).mean()), r["gain"], r["gain_c"], o["comp"]),
                          per_seed=[float(t_b - k_b[s]) for s in seeds])
        out[nm] = o
    return out


def interval(pt, two, comp_only, n_units):
    two = np.asarray(two, dtype=np.float64)
    se = float(np.std(two, ddof=1)) if len(two) > 1 else 0.0
    sec = float(np.std(comp_only, ddof=1)) if len(comp_only) > 1 else 0.0
    deff = (se * se) / (sec * sec) if sec > 0 else float("nan")
    lo, hi = (float(np.percentile(two, 2.5)), float(np.percentile(two, 97.5))) if len(two) else (pt, pt)
    lo90, hi90 = (float(np.percentile(two, 5)), float(np.percentile(two, 95))) if len(two) else (pt, pt)
    return dict(point=pt, lo=lo, hi=hi, lo90=lo90, hi90=hi90, se=se, se_comp=sec, deff=deff,
                n_eff=(n_units / deff) if deff == deff and deff > 0 else float("nan"), mde=2.8 * se)


# ── the words (HB-R5, HB-R6) ─────────────────────────────────────────────────────────────────────────────────────────────
def hb1_word(d, parity):
    if d["lo"] > 0:
        return "TREE-BETTER"
    if d["hi"] < 0:
        return "KMEANS-BETTER"
    if d["lo90"] >= -parity and d["hi90"] <= parity:
        return "PARITY"
    return "NEITHER"


def hb2_word(d):
    if d["lo"] > 0:
        return "DIVIDEND-TREE"
    if d["hi"] < 0:
        return "DIVIDEND-KMEANS"
    return "NEITHER"


def sign_word(d):
    """HB3: HB1's sign words only (no PARITY on EVAL)."""
    if d["lo"] > 0:
        return "TREE-BETTER"
    if d["hi"] < 0:
        return "KMEANS-BETTER"
    return "NEITHER"


def r1_word(ref, tau, xsrc):
    dt, dx = bool(tau != ref), bool(xsrc != ref)
    if dt and dx:
        return "FRAGILE-BOTH"
    if dt:
        return "FRAGILE-TAU"
    if dx:
        return "FRAGILE-XSRC"
    return "ROBUST"


def words_of(st, c):
    ALL, NX = st["boot"]["ALL"], st["boot"]["NO_XSRC"]
    w = dict(HB1=hb1_word(ALL["REF"]["final"], c["parity"]), HB2=hb2_word(ALL["REF"]["gain"]),
             HB1_TAU=hb1_word(ALL["TAU200"]["final"], c["parity"]), HB2_TAU=hb2_word(ALL["TAU200"]["gain"]),
             HB1_X=hb1_word(NX["REF"]["final"], c["parity"]), HB2_X=hb2_word(NX["REF"]["gain"]))
    w["R1"] = r1_word((w["HB1"], w["HB2"]), (w["HB1_TAU"], w["HB2_TAU"]), (w["HB1_X"], w["HB2_X"]))
    w["F_HB"] = bool(w["HB1"] == "KMEANS-BETTER")
    w["F_BR"] = bool(w["R1"] in ("FRAGILE-XSRC", "FRAGILE-BOTH"))
    return w


def brier_multi(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def pp(x):
    return "%+.2fpp" % (100.0 * x)


def iv(d, ninety=False):
    s = "%s [%s, %s] (%+.5f [%+.5f, %+.5f])" % (pp(d["point"]), pp(d["lo"]), pp(d["hi"]), d["point"], d["lo"], d["hi"])
    if ninety:
        s += " | 90%% [%+.5f, %+.5f]" % (d["lo90"], d["hi90"])
    return s


def median_tau(ts):
    xs = sorted(t for t in ts if t is not None)
    if not xs:
        return float("nan")
    k = len(xs)
    return float(xs[k // 2]) if k % 2 else 0.5 * (xs[k // 2 - 1] + xs[k // 2])


def cv_lines(st, c):
    """Every TRAIN-CV line of the outcome (HB1, HB2, R1, rule 8, F-HB, F-BR, predictions, descriptive); -> lines."""
    L = []
    w = st["words"]
    b = st["boot"]
    ALL = b["ALL"]
    df, dg = ALL["REF"]["final"], ALL["REF"]["gain"]
    L.append("=== HIER-FAIR-BACKOFF HB1 / HB2 (TRAIN-CV; %s) ===" % REG_TEXT)
    L.append(PILOT_SEEN)
    L.append("DENOMINATOR (Support (a)): %d TRAIN-CV items in %d CK-CLOSE components (registered 11,841 / 10,781; Kish mean component size"
             " %.4f); %d folds by component (salt %s; items per fold %s); %d k-means seeds; GATE %d key-complete items (tau only); CV"
             " bootstrap B %d, default_rng(%d)" % (st["n"], st["comp"], st["kish"], c["nfold"], c["fold_salt"],
                                                   "/".join(str(x) for x in st["fold_sizes"]), len(c["kseeds"]), st["n_gate"], c["B_cv"],
                                                   c["cv_seed"]))
    L.append("LIKE WITH LIKE: TF / TB AF-U flat / back-off [SC] | BCF_s / BCB_s shape-matched spherical k-means hierarchy, per-level node"
             " counts %s (= AF-U's, every seed), filing nearest leaf centroid over all leaves [SC] | KWF_s the K_s cells (flat, %s"
             " cells) [SC]; only the cells' content differs between TB and BCB" % (st["shape"], "/".join(str(x) for x in st["kwf_cells"])))
    L.append("ARMS (TRAIN-CV accuracy): BEST %.5f | TF %.5f | TB %.5f | TB200 %.5f | BCF_s %s | BCB_s %s | BCB200_s %s | KWF_s %s" % (
        ALL["acc"][("BEST", "F")], ALL["acc"][("AF", "F")], ALL["acc"][("AF", "B")], ALL["acc"][("AF", "B200")],
        " / ".join("%.5f" % ALL["acc"][("BC%d" % s, "F")] for s in range(st["nseeds"])),
        " / ".join("%.5f" % ALL["acc"][("BC%d" % s, "B")] for s in range(st["nseeds"])),
        " / ".join("%.5f" % ALL["acc"][("BC%d" % s, "B200")] for s in range(st["nseeds"])),
        " / ".join("%.5f" % ALL["acc"][("KW%d" % s, "F")] for s in range(st["nseeds"]))))
    L.append("HB1 (DECIDING; the 95%% interval decides the sign words, the 90%% interval the parity word): D_final = acc(TB) - mean_s"
             " acc(BCB_s) = %s" % iv(df, True))
    L.append("  support D_final: n %d in %d components, SE %.5f (registered planning 0.00195), component-only SE %.5f, DEFF %.3f"
             " (registered 1.61, measured in the pilot), n_eff %.0f (registered 6,696), MDE80 %s (registered 0.55pp); TOST at +/-0.60pp"
             " needs 0.60 - |predicted| >= 2.487 SE: %.5f; %s" % (st["n"], st["comp"], df["se"], df["se_comp"], df["deff"],
                                                                 df["n_eff"], pp(df["mde"]), 2.487 * df["se"], VERDICT_HB))
    v = w["HB1"]
    hit("HB1." + v)
    L.append("  HB1 -> %s (%s)" % (v, {
        "TREE-BETTER": "the 95%% lower bound %+.5f > 0" % df["lo"],
        "KMEANS-BETTER": "the 95%% upper bound %+.5f < 0" % df["hi"],
        "PARITY": "neither sign word; the 90%% interval [%+.5f, %+.5f] lies inside [-%.4f, +%.4f]" % (df["lo90"], df["hi90"], c["parity"], c["parity"]),
        "NEITHER": "neither sign word; the 90%% interval [%+.5f, %+.5f] leaves [-%.4f, +%.4f]" % (df["lo90"], df["hi90"], c["parity"], c["parity"])}[v]))
    L.append("HB2 (DECIDING; the 95%% interval decides): D_gain = [acc(TB) - acc(TF)] - mean_s [acc(BCB_s) - acc(BCF_s)] = %s" % iv(dg))
    L.append("  support D_gain: SE %.5f (registered planning 0.00220), component-only SE %.5f, DEFF %.3f (registered 1.56), n_eff %.0f"
             " (registered 6,911), MDE80 %s (registered 0.62pp)" % (dg["se"], dg["se_comp"], dg["deff"], dg["n_eff"], pp(dg["mde"])))
    hit("HB2." + w["HB2"])
    L.append("  HB2 -> %s" % w["HB2"])
    if w["HB2"] == "DIVIDEND-TREE" and v == "PARITY":
        L.append("  WORDS FIXED NOW (registered): a positive D_gain beside HB1 PARITY says the tree's flat leaves route worse and its"
                 " back-off recovers the difference; it is never read as 'the tree's hierarchy is better than k-means'")
    if v != "PARITY":
        hit("R8.PARITY_REFUTED")
        L.append("RULE 8: PARITY is REFUTED (HB1 %s: %s)" % (v, "a sign word" if v in ("TREE-BETTER", "KMEANS-BETTER")
                                                                 else "the 90% interval leaves +/-0.60pp"))
    else:
        hit("R8.PARITY_NOT")
        L.append("RULE 8: PARITY is not refuted (the 90% interval inside +/-0.60pp, no sign word)")
    L.append("RULE 8: TREE-BETTER is %s (95%% lower bound %+.5f %s 0)" % ("REFUTED" if df["lo"] <= 0 else "not refuted", df["lo"],
                                                                         "<=" if df["lo"] <= 0 else ">"))
    L.append("RULE 8: DIVIDEND-TREE is %s (95%% lower bound %+.5f %s 0)" % ("REFUTED" if dg["lo"] <= 0 else "not refuted", dg["lo"],
                                                                           "<=" if dg["lo"] <= 0 else ">"))
    if w["F_HB"]:
        hit("FHB.FIRED")
        L.append(FHB_FIRES)
    else:
        hit("FHB.NOT")
        L.append("FALSIFIER F-HB: NOT FIRED (HB1 %s; F-HB fires iff KMEANS-BETTER)" % v)
    L.append("TAU (GATE, per fold): tau*(AF-U) %s (median %s) | BC_s %s" % (
        " ".join(str(t) for t in st["tstar"]["AF"]), _g(median_tau(st["tstar"]["AF"])),
        " | ".join("s%d %s" % (s, " ".join(str(t) for t in st["tstar"]["BC%d" % s])) for s in range(st["nseeds"]))))
    L.append("DESCRIPTIVE: per seed D_final %s; KWF mean %.5f; flat tree minus flat shape-matched %s" % (
        " / ".join("%+.5f" % x for x in ALL["REF"]["per_seed"]), float(np.mean([ALL["acc"][("KW%d" % s, "F")] for s in range(st["nseeds"])])),
        "%+.5f" % (ALL["acc"][("AF", "F")] - float(np.mean([ALL["acc"][("BC%d" % s, "F")] for s in range(st["nseeds"])])))))
    for nm in sorted(b):
        if nm in ("ALL",):
            continue
        o = b[nm]
        L.append("DESCRIPTIVE: %-14s n %5d (%d components): D_final %s | D_gain %s" % (nm, o["n"], o["comp"], iv(o["REF"]["final"]),
                                                                                      iv(o["REF"]["gain"])))
    L.append("DESCRIPTIVE: BC_s build: degenerate splits %s, empty leaves %s" % (
        "/".join(str(x["degenerate"]) for x in st["bc_info"]), "/".join(str(x["empty"]) for x in st["bc_info"])))
    # predictions
    for lab, x, band in (("P1 D_final -0.05pp [-0.40, +0.30]", df["point"], PRED["P1"]), ("P3 D_gain +0.50pp [+0.10, +0.90]", dg["point"], PRED["P3"])):
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION %s: observed %+.5f -> %s" % (lab, x, "HELD" if ok else "FAILED"))
    L.append("PREDICTION P2 HB1 PARITY 0.70, NEITHER 0.20, KMEANS-BETTER 0.07, TREE-BETTER 0.03: observed %s; Brier %.4f" % (
        v, brier_multi(PRED["P2"], v)))
    L.append("PREDICTION P4 HB2 DIVIDEND-TREE 0.80, NEITHER 0.20, DIVIDEND-KMEANS 0.00: observed %s; Brier %.4f" % (
        w["HB2"], brier_multi(PRED["P4"], w["HB2"])))
    mt = median_tau(st["tstar"]["AF"])
    ok = bool(mt == mt and U.in_band(mt, PRED["P6"]))
    hit("PRED.HELD" if ok else "PRED.FAILED")
    L.append("PREDICTION P6 median over folds of tau*(AF-U) in [50, 200]: observed %s -> %s" % (_g(mt), "HELD" if ok else "FAILED"))
    # BACKOFF-ROBUST
    tf, tg = ALL["TAU200"]["final"], ALL["TAU200"]["gain"]
    xf, xg = b["NO_XSRC"]["REF"]["final"], b["NO_XSRC"]["REF"]["gain"]
    L.append("=== BACKOFF-ROBUST R1 (the robustness legs of HIER-FAIR-BACKOFF; same tool, folds, seeds and bootstrap) ===")
    L.append("TAU200 (tau 200 for TB and BCB in every fold and seed): D_final %s -> HB1 %s | D_gain %s -> HB2 %s" % (
        iv(tf, True), w["HB1_TAU"], iv(tg), w["HB2_TAU"]))
    L.append("  support TAU200: n %d / %d components, SE %.5f (registered 0.00147), DEFF %.3f, MDE80 %s (registered 0.41pp)" % (
        st["n"], st["comp"], tf["se"], tf["deff"], pp(tf["mde"])))
    L.append("NO-XSRC (scored on the %d items AF-U files into a leaf of their own source; %d cross-source filings removed, per fold %s;"
             " the pilot counted 311): D_final %s -> HB1 %s | D_gain %s -> HB2 %s" % (
                 b["NO_XSRC"]["n"], st["n_xsrc"], "/".join(str(x) for x in st["xsrc_fold"]), iv(xf, True), w["HB1_X"], iv(xg), w["HB2_X"]))
    L.append("  support NO-XSRC: n %d / %d components, SE %.5f (registered 0.00198), DEFF %.3f, MDE80 %s (registered 0.55pp); %s" % (
        b["NO_XSRC"]["n"], b["NO_XSRC"]["comp"], xf["se"], xf["deff"], pp(xf["mde"]), VERDICT_BR))
    hit("R1." + w["R1"])
    L.append("R1 (DECIDING): %s (reference (HB1, HB2) = (%s, %s); TAU200 (%s, %s); NO-XSRC (%s, %s))" % (
        w["R1"], w["HB1"], w["HB2"], w["HB1_TAU"], w["HB2_TAU"], w["HB1_X"], w["HB2_X"]))
    if w["R1"] == "ROBUST":
        L.append("RULE 8 (BACKOFF-ROBUST): ROBUST is not refuted (no word changed)")
    else:
        L.append("RULE 8 (BACKOFF-ROBUST): ROBUST is REFUTED (a word changed: %s)" % w["R1"])
    if w["F_BR"]:
        hit("FBR.FIRED")
        L.append(FBR_FIRES % w["R1"])
    else:
        hit("FBR.NOT")
        L.append("FALSIFIER F-BR: NOT FIRED (R1 %s; F-BR fires iff FRAGILE-XSRC or FRAGILE-BOTH)%s" % (
            w["R1"], "; HIER-FAIR-BACKOFF's words are quoted 'at the GATE-chosen tau only'" if w["R1"] == "FRAGILE-TAU" else ""))
    for lab, x, band in (("P1 TAU200 D_final -0.45pp [-0.80, -0.10]", tf["point"], PRED_BR["P1"]),
                         ("P2 NO-XSRC D_final -0.08pp [-0.45, +0.30]", xf["point"], PRED_BR["P2"])):
        ok = U.in_band(x, band)
        hit("PRED.HELD" if ok else "PRED.FAILED")
        L.append("PREDICTION (BACKOFF-ROBUST) %s: observed %+.5f -> %s" % (lab, x, "HELD" if ok else "FAILED"))
    L.append("PREDICTION (BACKOFF-ROBUST) P1 HB1 under TAU200 KMEANS-BETTER 0.60, NEITHER 0.30, PARITY 0.10: observed %s; Brier %.4f" % (
        w["HB1_TAU"], brier_multi(PRED_BR["P1W"], w["HB1_TAU"])))
    eq = bool(w["HB1_X"] == w["HB1"])
    L.append("PREDICTION (BACKOFF-ROBUST) P2 NO-XSRC HB1 word equal to the reference (probability 0.80): %s vs %s -> %s; Brier %.4f" % (
        w["HB1_X"], w["HB1"], "TRUE" if eq else "FALSE", (PRED_BR["P2EQ"] - float(eq)) ** 2))
    L.append("PREDICTION (BACKOFF-ROBUST) P3 R1 FRAGILE-TAU 0.55, ROBUST 0.30, FRAGILE-BOTH 0.10, FRAGILE-XSRC 0.05: observed %s; Brier %.4f"
             % (w["R1"], brier_multi(PRED_BR["P3"], w["R1"])))
    L.append(WNS_BR)
    return L


def _g(x):
    return "n/a" if x != x else ("%g" % x)


def hb3_lines(h3, c):
    L = []
    df, dg = h3["final"], h3["gain"]
    L.append("=== HB3 (SCORED SECONDARY; DESCRIPTIVE-ONLY by Support; EVAL, unseen data) ===")
    L.append("DENOMINATOR: %d EVAL items in %d components (registered 5,907 / 5,404); TRAIN-fitted policies; tau* on GATE per arm: AF-U %s |"
             " BC_s %s; B %d two-stage replicates (tree_backoff's run_boot hook, default_rng(%d))" % (
                 h3["n"], h3["comp"], h3["tstar"]["AF"], " / ".join(str(h3["tstar"]["K%d" % s]) for s in range(5)), c["B"], c["seed"]))
    L.append("ARMS (EVAL accuracy, point): BEST %.5f | TF %.5f | TB %.5f | BCF_s %s | BCB_s %s" % (
        h3["acc"]["BEST"], h3["acc"]["TF"], h3["acc"]["TB"], " / ".join("%.5f" % x for x in h3["bcf"]), " / ".join("%.5f" % x for x in h3["bcb"])))
    sw = sign_word(df)
    hit("HB3." + sw)
    L.append("HB3 D_final = %s (point +- 1.96 SE_2stage; SE %.5f, DEFF %s, MDE80 %s; registered SE 0.441pp, MDE80 1.23pp) -> %s"
             " (descriptive)" % (iv(df), df["se2"], _f(df["deff"]), pp(df["mde"]), sw))
    L.append("HB3 D_gain = %s -> %s (descriptive)" % (iv(dg), hb2_word(dg)))
    nx = h3["final_nx"]
    L.append("HB3 NO_XSRC (the %d EVAL items AF-U files into another source's leaf removed; registered 191): D_final %s (descriptive)" % (
        h3["n_xsrc"], iv(nx)))
    ok = U.in_band(df["point"], PRED["P5"])
    hit("PRED.HELD" if ok else "PRED.FAILED")
    L.append("PREDICTION P5 (HB3) D_final -0.30pp [-1.30, +0.70]: observed %+.5f -> %s" % (df["point"], "HELD" if ok else "FAILED"))
    return L


def _f(x):
    return "n/a" if x != x else "%.3f" % x


# ── the deciding TRAIN-CV path (run() calls it between the TRAIN key and the eval view; the selftest calls it on fixtures) ────
def train_cv(P_, K_tr, train_meta, models, gk, gitems, c, say):
    """-> st: the TRAIN-CV scored set, the folds, the arms, every column, tau*, the bootstrap and the words (no EVAL item)."""
    af, vec = P_["af"], P_["vec"]
    items = sorted(i for i in V.complete_items(K_tr, models)
                   if i in train_meta and af.get(i) is not None and af[i] not in PSEUDO and i in vec)
    if set(items) & set(gitems):
        hit("REFUSE.GATE_SIDE")
        refuse("[HFB-GATE-SIDE] %d GATE item(s) among the TRAIN-CV items" % len(set(items) & set(gitems)))
    comp = [train_meta[i][0] for i in items]
    n_c = len(set(comp))
    if (len(items), n_c) != (c["n_cv"], c["comp_cv"]):
        hit("REFUSE.CV_DENOM")
        refuse("[HFB-CV-DENOM] the TRAIN-CV scored set is %d items / %d components, not the registered %d / %d" % (
            len(items), n_c, c["n_cv"], c["comp_cv"]))
    m = len(models)
    A = np.array([[K_tr[i][mm] for mm in models] for i in items], dtype=np.int64).reshape(len(items), m)
    strat = [train_meta[i][1] for i in items]
    own = np.array([UCI.cell_member(af[i]) == strat[j] for j, i in enumerate(items)], dtype=bool)
    fold = np.array([fold_of(x, c["fold_salt"], c["nfold"]) for x in comp], dtype=np.int64)
    Kg = np.array([[gk[i][mm] for mm in models] for i in gitems], dtype=np.int64).reshape(len(gitems), m)
    arms = {"AF": TB.Arm("AF-U", P_["H_af"], [af[i] for i in items], [P_["gcell"][i] for i in gitems], m)}
    for s in c["kseeds"]:
        fl = P_["bc_file"][s]
        arms["BC%d" % s] = TB.Arm("BC%d" % s, P_["H_bc"][s], [fl(vec[i]) for i in items], [fl(vec[i]) for i in gitems], m)
    kw = {}
    kwf_cells = []
    for s in c["kseeds"]:
        kc = P_["kx"]["K%d" % s]
        cells = [kc.get(i, V.NO_ROUTING_ROW) for i in items]
        h = flat_hier("KWF%d" % s, cells)
        kw["KW%d" % s] = TB.Arm("KWF%d" % s, h, cells, [], m)
        kwf_cells.append(len(set(cells)))
    cols, tstar = cv_predict(A, fold, arms, kw, Kg, list(c["taus"]), c["nfold"], c["tau_fixed"])
    srcs = sorted(set(strat))
    masks = [("ALL", np.ones(len(items), dtype=bool)), ("NO_XSRC", own), ("NON_BBH", np.array([s != "BBH" for s in strat], dtype=bool))]
    masks += [("SRC:" + s, np.array([x == s for x in strat], dtype=bool)) for s in srcs]
    boot = cv_boot(cols, comp, masks, c["B_cv"], c["cv_seed"], len(c["kseeds"]))
    st = dict(n=len(items), comp=n_c, kish=UCI.kish(Counter(comp).values()), fold_sizes=[int((fold == f).sum()) for f in range(c["nfold"])],
              n_gate=len(gitems), shape=P_["shape"], kwf_cells=kwf_cells, nseeds=len(c["kseeds"]), tstar=tstar, boot=boot,
              n_xsrc=int((~own).sum()), xsrc_fold=[int(((fold == f) & ~own).sum()) for f in range(c["nfold"])], bc_info=P_["bc_info"],
              items=items, cols=cols, fold=fold, own=own)
    st["words"] = words_of(st, c)
    return st


# ── HB3 (EVAL; descriptive) ──────────────────────────────────────────────────────────────────────────────────────────────
def hb3_arms(D, P_, gitems, c):
    m = len(D.models)
    arms = {"AF": TB.Arm("AF-U", P_["H_af"], [D.tree_keys[g] for g in D.g_tree], [P_["gcell"][i] for i in gitems], m)}
    for j, s in enumerate(c["kseeds"]):
        fl = P_["bc_file"][s]
        pos = []
        for k, i in enumerate(D.items):
            a = D.tree_keys[D.g_tree[k]]
            if a in PSEUDO:
                pos.append(a)
            elif i in P_["vec"]:
                pos.append(fl(P_["vec"][i]))
            else:
                refuse("[HFB-VEC] scored item %s has an AF-U leaf but no vector" % i)
        arms["K%d" % j] = TB.Arm("BC%d" % s, P_["H_bc"][s], pos, [fl(P_["vec"][i]) for i in gitems], m)
    return arms


def hb3(D, arms, Kg, c, after_boot):
    """TREE-BACKOFF's two-stage reader with the BC arms in the K columns -> h3 dict; the [HFB-MIRROR] check on TF / BEST."""
    taus = {nm: TB.choose_tau(D, arms[nm], Kg, list(c["taus"])) for nm in TB.ARMS}
    tstar = {nm: taus[nm][0] for nm in TB.ARMS}
    masks, n_xsrc = TB.masks_of(D, arms["AF"])
    two_rows = []

    def hook(D_, wt, v):
        CE, _pk = TB.arm_matrix(D_, arms, tstar, wt)
        two_rows.append(TB.score(CE, v, masks))
    bt = V.run_boot(D, c["B"], c["seed"], hook=hook)
    after_boot(bt)
    if len(two_rows) != c["B"]:
        refuse("[HFB-HOOK] the hook ran %d times, not B %d" % (len(two_rows), c["B"]))
    NE = len(D.E)
    CE0, _pk0 = TB.arm_matrix(D, arms, tstar, V.train_full(D))
    point = TB.score(CE0, np.ones(NE), masks)
    iid = np.stack([TB.score(CE0, vi, masks) for vi in U.iid_weights(c["seed"], NE, c["B"])])
    two = np.stack(two_rows)
    ns = len(D.subsets)
    for mine, theirs in ((TB.TF, V.TREE), (TB.BEST, V.BS)):
        for lab, a, b_ in (("point", point[:ns, mine], bt["point"][:, theirs]), ("two-stage", two[:, :ns, mine], bt["two"][:, :, theirs])):
            if a.shape != b_.shape or not np.allclose(a, b_, rtol=0.0, atol=1e-12, equal_nan=True):
                hit("REFUSE.MIRROR")
                refuse("[HFB-MIRROR] the hook's column %d differs from run_boot's arm %d (%s)" % (mine, theirs, lab))
    names = [nm for nm, _m in masks]

    def lin(wv, sub="ALL"):
        j = names.index(sub)
        return U.interval(float(point[j] @ wv), two[:, j, :] @ wv, iid[:, j, :] @ wv, int(masks[j][1].sum()))
    wf = np.zeros(TB.NCOL)
    wf[TB.TB] = 1.0
    wf[TB.KB0:TB.KB0 + 5] -= 0.2
    wg = np.zeros(TB.NCOL)
    wg[TB.TB] += 1.0
    wg[TB.TF] -= 1.0
    wg[TB.KB0:TB.KB0 + 5] -= 0.2
    wg[TB.KF0:TB.KF0 + 5] += 0.2
    return dict(n=NE, comp=D.eval_units["n_units"], tstar=tstar, final=lin(wf), gain=lin(wg), final_nx=lin(wf, "NO_XSRC"), n_xsrc=n_xsrc,
                acc=dict(TF=float(point[0, TB.TF]), TB=float(point[0, TB.TB]), BEST=float(point[0, TB.BEST])),
                bcf=[float(point[0, TB.KF0 + s]) for s in range(5)], bcb=[float(point[0, TB.KB0 + s]) for s in range(5)], bt=bt)


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def files():
    return [os.path.abspath(__file__), TB.__file__, U.__file__, EC.__file__] + [os.path.join(HERE, n) for n, _ in U.PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered Support (a)-(e)): TRAIN-CV %d items in %d CK-CLOSE components; DEFF 1.61 (D_final) / 1.56 (D_gain)"
        " measured in the pilot, n_eff 6,696 / 6,911, planning SE 0.195pp / 0.220pp, MDE80 0.55pp / 0.62pp; PARITY margin +/-0.60pp"
        " (TOST need 0.485pp, met); HB3 EVAL %d / %d (MDE80 1.23pp); %s" % (c["n_cv"], c["comp_cv"], c["n_route"], c["comp_route"], VERDICT_HB))
    say("PLANNED: %d folds (salt %s); tau grid %s per arm, seed and fold on the %d key-complete GATE items; TAU200 = tau %d; arms TF, TB,"
        " BCF_s, BCB_s (s = %s), KWF_s; CV bootstrap B %d default_rng(%d) (components, then seeds); HB3 run_boot B %d default_rng(%d)" % (
            c["nfold"], c["fold_salt"], "/".join(str(t) for t in c["taus"]), c["n_gate_key"], c["tau_fixed"],
            "/".join(str(s) for s in c["kseeds"]), c["B_cv"], c["cv_seed"], c["B"], c["seed"]))
    say("COST: 0 calls, 0 CCE; CPU: 5 shape-matched hierarchies; TRAIN-CV %d back-off fits (%d folds x 6 arms x %d taus) + KWF; CV"
        " bootstrap; HB3 run_boot with an 11-arm hook (B %d)" % (c["nfold"] * 6 * len(c["taus"]), c["nfold"], len(c["taus"]), c["B"]))
    say("IDENTITY TARGETS (UNION-AF-ROUTE outcome sha256 %s): %s" % (c["uar_outcome_sha"][:16], U.identity_text(c["identity"])))


def prepare(say):
    """Everything before any key: union_route_common.prepare, AF-U, the bundle's TRAIN rows, BC_s (shape checked), vectors, GATE cells."""
    c = reg()
    S = U.prepare(say, c, refuse, hit)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    Xt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)])
    titems = [str(x) for x in b["train_item"]]
    side, _smeta = UAR._SIDES[0]()
    rows_h, rows_t = ERC.item_rows(ip["merged"] if S["single"] else UAR.afu_paths(S["single"])[1])
    gits, gcell, _gs = ERC.gate_items(rows_h, side)
    if not gits:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: tau* is undefined")
    H_af = TB.af_hier(u["members"], u["afu"], S["single"])
    say("  AF-U HIERARCHY (tree_backoff R1): %s; per-level node counts %s" % (H_af.summary(), level_counts(H_af)))
    under = np.zeros(H_af.N)
    for i in titems:
        cl = S["af"].get(i)
        if cl is not None and cl in H_af.idx:
            under += H_af.M[:, H_af.idx[cl]]
    ids = sorted(set(i for i, cl in S["af"].items() if cl != V.NO_ROUTING_ROW) | set(gits))
    vec = ERC.get_vectors(ids)
    nov = [i for i in ids if i not in vec]
    if nov:
        refuse("%d item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(vec, b)
    H_bc, bc_file, bc_info = {}, {}, []
    shape = None
    for s in c["kseeds"]:
        h, C, cn, info = bc_build(H_af, Xt, tsrc, u["sources"], S["single"], s, under)
        shape = check_shape(H_af, h, "BC%d" % s)
        H_bc[s], bc_file[s] = h, filer(C, cn)
        bc_info.append(info)
        say("  BC%d (HB-R1): %s; per-level node counts %s = AF-U's; %d leaf centroids; degenerate splits %d, empty leaves %d" % (
            s, h.summary(), level_counts(h), len(cn), info["degenerate"], info["empty"]))
    say("  vectors equal to the bundle's on %d items; GATE items with a routing row %d (modal AF leaf; BC cells by nearest centroid)"
        % (nb, len(gits)))
    return dict(S, H_af=H_af, H_bc=H_bc, bc_file=bc_file, bc_info=bc_info, shape=shape, gits=gits, gcell=gcell, vec=vec)


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    denominators(say)
    P_ = prepare(say)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    say("OUTPUTS (write-once, never committed): %s, %s" % (reg()["out"], reg()["marker"]))
    say("DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL); no statistic printed.")
    hit("DRY.DONE")
    return 0


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, files())
    for p in (c["out"], c["marker"]):
        if os.path.exists(U.P(p)):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    denominators(say)
    P_ = prepare(say)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    if int(cfg.reg["B"]) != int(c["B"]) or int(cfg.reg["seed"]) != int(c["seed"]):
        refuse("the reader's B / seed %s / %s are not the registered %s / %s" % (cfg.reg["B"], cfg.reg["seed"], c["B"], c["seed"]))
    box = {}

    def between(K_tr, train_meta, models):
        K, comp, _meta = EC.gate_key(cfg, say, models, P_["gits"])
        gitems = sorted(i for i in comp if i in P_["gcell"])
        if len(gitems) != int(c["n_gate_key"]):
            hit("REFUSE.GATE_DENOM")
            refuse("[HFB-GATE-DENOM] %d key-complete GATE items with a cell, not the registered %d" % (len(gitems), c["n_gate_key"]))
        if set(gitems) & set(train_meta):
            hit("REFUSE.GATE_SIDE")
            refuse("[HFB-GATE-SIDE] %d GATE item(s) on the TRAIN side" % len(set(gitems) & set(train_meta)))
        box["gitems"], box["gk"] = gitems, K
        box["st"] = train_cv(P_, K_tr, train_meta, models, K, gitems, c, say)
        say("  TRAIN-CV computed BEFORE the eval view opened: %d items / %d components; HB1 %s, HB2 %s, R1 %s are fixed here" % (
            box["st"]["n"], box["st"]["comp"], box["st"]["words"]["HB1"], box["st"]["words"]["HB2"], box["st"]["words"]["R1"]))
    D, ok_sha = U.read_views(cfg, say, False, P_["af"], P_["kx"], c["marker"],
                             "HIER-FAIR-BACKOFF: the EVAL key read started (HB3). frozen policy sha256 %s" % c["uar_policy_sha"], refuse, hit,
                             between=between, tag=TEST_ID)
    n_comp = U.check_denominators(D, c, refuse, hit, "HFB")
    say("  scored: TRAIN %d, EVAL %d key-complete items in %d components" % (D.n_train, D.n_eval, n_comp))
    U.b3_check(D, cfg, P_["pol"], refuse, hit)
    say("  B3: the point policy re-fitted beside EVAL equals the frozen file")
    gitems = box["gitems"]
    Kg = np.array([[box["gk"][i][m] for m in D.models] for i in gitems], dtype=np.int64)
    arms = hb3_arms(D, P_, gitems, c)

    def after_boot(bt):
        ok, got = U.identity(bt, D, c["identity"])
        if not ok:
            hit("REFUSE.IDENTITY")
            refuse("[HFB-IDENTITY] %s is not UNION-AF-ROUTE's %s" % (U.identity_text(got), U.identity_text(c["identity"])))
        say("IDENTITY: %s -> REPRODUCED (UNION-AF-ROUTE's printed digits)" % U.identity_text(got))
        hit("IDENTITY.OK")
    h3 = hb3(D, arms, Kg, c, after_boot)
    say("  MIRROR: the hook's TF / BEST equal run_boot's TREE / best single at the point and in every replicate")
    st = box["st"]
    for ln in cv_lines(st, c) + hb3_lines(h3, c):
        say(ln)
    say("WORDS: every arm SOURCE-CONDITIONED [SC], never label-free; key-scored, no judge verdict (no wrong(established) count, no tie"
        " convention A / B); tau* held at its GATE choice per fold (GATE selection variance not propagated); one tree, one draw, one roster")
    say(WNS)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    hit("RUN.DONE")
    return dict(st=st, h3=h3, D=D, arms=arms, Kg=Kg, gitems=gitems, P=P_)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=None, help="the checkout whose results / views / caches are read (set before any import)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return run_mutants(only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

import io            # noqa: E402
import re            # noqa: E402
import types         # noqa: E402
import contextlib    # noqa: E402
from collections import defaultdict   # noqa: E402

BRANCHES = ("HB1.TREE-BETTER", "HB1.KMEANS-BETTER", "HB1.PARITY", "HB1.NEITHER", "HB2.DIVIDEND-TREE", "HB2.DIVIDEND-KMEANS",
            "HB2.NEITHER", "R1.ROBUST", "R1.FRAGILE-TAU", "R1.FRAGILE-XSRC", "R1.FRAGILE-BOTH", "FHB.FIRED", "FHB.NOT", "FBR.FIRED",
            "FBR.NOT", "R8.PARITY_REFUTED", "R8.PARITY_NOT", "HB3.TREE-BETTER", "HB3.KMEANS-BETTER", "HB3.NEITHER", "PRED.HELD",
            "PRED.FAILED", "IDENTITY.OK", "RUN.DONE", "DRY.DONE", "MARKER.WRITTEN", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.SHAPE",
            "REFUSE.CV_DENOM", "REFUSE.GATE_DENOM", "REFUSE.GATE_SIDE", "REFUSE.IDENTITY", "REFUSE.DENOM", "REFUSE.MIRROR")
need = U.need


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


# ── the independent loop oracle ────────────────────────────────────────────────────────────────────────────────────────────
def _argmax_first(xs):
    best, bj = None, 0
    for j, x in enumerate(xs):
        if best is None or x > best:
            best, bj = x, j
    return bj


def _o_pol(par, cell, fit_w, K, mu, tau):
    """Plain-loop back-off on a parent map: fit_w = {item: weight}; -> (pick(leaf) -> model index, best single index)."""
    m = len(mu)
    S = defaultdict(lambda: [0.0] * m)
    N = defaultdict(float)
    for i, w in fit_w.items():
        if not w:
            continue
        v = cell[i]
        while v is not None:
            N[v] += w
            row = S[v]
            for j in range(m):
                row[j] += w * K[i][mu[j]]
            v = par[v]
    root = [v for v, p in par.items() if p is None][0]
    best = _argmax_first(S[root])
    memo = {}

    def p(v):
        if v not in memo:
            if par[v] is None:
                memo[v] = [S[v][j] / N[v] for j in range(m)]
            else:
                pp_ = p(par[v])
                memo[v] = [(S[v][j] + tau * pp_[j]) / (N[v] + tau) for j in range(m)]
        return memo[v]

    def pick(leaf):
        if tau == 0:
            return best if N[leaf] < 1 else _argmax_first(S[leaf])
        return _argmax_first(p(leaf))
    return pick, best


def _o_bc(par, Xt, tsrc, sources, single_cells, seed, train_cells):
    """Independent BC_s: own children / leaf counts / TRAIN-under counts from the parent map; GB.ukm_fit (the instrument) per split."""
    kids = defaultdict(list)
    for v, p in par.items():
        if p is not None:
            kids[p].append(v)
    lcm = {}

    def lc(v):
        if v not in lcm:
            lcm[v] = 1 if not kids[v] else sum(lc(c) for c in kids[v])
        return lcm[v]
    under = defaultdict(int)
    for cl in train_cells:
        v = cl
        while v is not None and v in par:
            under[v] += 1
            v = par[v]
    cents, bpar = {}, {UNION: None}
    for so in sources:
        rows = [j for j in range(len(tsrc)) if tsrc[j] == so]
        if so in single_cells:
            nm = "BC%d|%s" % (seed, single_cells[so])
            bpar[nm] = UNION
            if rows:
                s_ = Xt[rows].sum(axis=0)
                cents[nm] = s_ / np.linalg.norm(s_)
            continue
        root = [v for v in kids[UNION] if v.startswith(so + ":") and v != single_cells.get(so)][0]
        todo = [(root, rows, UNION)]
        while todo:
            v, idx, pr = todo.pop(0)
            nm = "BC%d|%s" % (seed, v)
            bpar[nm] = pr
            if not kids[v]:
                if idx:
                    s_ = Xt[idx].sum(axis=0)
                    cents[nm] = s_ / np.linalg.norm(s_)
                continue
            k = len(kids[v])
            if k == 1:
                lab = [0] * len(idx)
            elif len(idx) > k:
                lab = [int(x) for x in GB.ukm_fit(Xt[idx], k, seed)[0]["labels"]]
            else:
                lab = list(range(len(idx)))
            size = [sum(1 for x in lab if x == j) for j in range(k)]
            corder = sorted(range(k), key=lambda j: (-size[j], j))
            korder = sorted(kids[v], key=lambda c: (-lc(c), -under[c], c))
            for c, j in zip(korder, corder):
                todo.append((c, [idx[q] for q in range(len(idx)) if lab[q] == j], nm))
    for p in PSEUDO:
        bpar[p] = UNION

    def depth(v):
        d = 0
        while bpar[v] is not None:
            v, d = bpar[v], d + 1
        return d
    dm = max(depth(v) for v in bpar)
    levels = [sum(1 for v in bpar if depth(v) == d and v not in PSEUDO) for d in range(1, dm + 1)]
    return cents, bpar, levels


def _o_file(cents, x):
    best, bn = None, None
    for nm, cv in cents.items():
        s_ = float(np.dot(cv, x))
        if best is None or s_ > best:
            best, bn = s_, nm
    return bn


def _o_iv(pt, reps):
    return dict(point=pt, lo=float(np.percentile(reps, 2.5)), hi=float(np.percentile(reps, 97.5)), lo90=float(np.percentile(reps, 5)),
                hi90=float(np.percentile(reps, 95)), se=float(np.std(reps, ddof=1)))


def _o_hb1(d, par_=0.0060):
    return "TREE-BETTER" if d["lo"] > 0 else ("KMEANS-BETTER" if d["hi"] < 0 else (
        "PARITY" if (d["lo90"] >= -par_ and d["hi90"] <= par_) else "NEITHER"))


def _o_hb2(d):
    return "DIVIDEND-TREE" if d["lo"] > 0 else ("DIVIDEND-KMEANS" if d["hi"] < 0 else "NEITHER")


def _oracle(lay, res, c):
    """TRAIN-CV by loops: the scored set, folds, BC_s, filings, every fold's picks and GATE tau*, the two-stage replay, the words;
    HB3's point arms and SE by a replay of run_boot's unit draws."""
    fx = lay.fx
    mu, K, man, af, par, tr = TB._o_af(lay)
    b, _m = GC.load_bundle(os.path.join(lay.tmp, "res", "inputs", "af_u_bundle_256"), expect=None)
    Xt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    classes = [str(x) for x in b["classes"]]
    tsrc = [UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)]
    titems = [str(x) for x in b["train_item"]]
    single_cells = {so: cl for cl in set(af.values()) for so in [cl.split(":")[0]] if par.get(cl) == UNION and cl not in PSEUDO}
    gk = TB._o_gate_key(fx.spec, sorted(lay.gate_cells))
    gitems = sorted(gk)
    items = sorted(i for i in tr if af[i] not in PSEUDO and i in fx.vec)
    comp = {i: fx.side[i][0] for i in items}
    src = {i: fx.strata[i][0] for i in items}
    own = {i: af[i].split(":")[0] == src[i] for i in items}
    fold = {i: int(hashlib.sha256((comp[i] + c["fold_salt"]).encode("utf-8")).hexdigest(), 16) % c["nfold"] for i in items}
    arms = {"AF": (par, dict(af), {g: lay.gate_cells[g] for g in gitems})}
    levels = {}
    for s in c["kseeds"]:
        cents, bpar, lev = _o_bc(par, Xt, tsrc, fx.reg["sources"], single_cells, s, [af[i] for i in titems if i in af])
        levels[s] = lev
        cell = {i: _o_file(cents, fx.vec[i]) for i in items}
        arms["BC%d" % s] = (bpar, cell, {g: _o_file(cents, fx.vec[g]) for g in gitems})
    kws = {}
    for s in c["kseeds"]:
        kc, _ = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "k_cells_s%d.tsv" % s), man["inputs"]["res/inputs/k_cells_s%d.tsv" % s])
        kpar = {UNION: None}
        for i in items:
            kpar[kc.get(i, V.NO_ROUTING_ROW)] = UNION
        kws["KW%d" % s] = (kpar, {i: kc.get(i, V.NO_ROUTING_ROW) for i in items})
    col = defaultdict(dict)
    tst = defaultdict(list)
    for f in range(c["nfold"]):
        ho = [i for i in items if fold[i] == f]
        if not ho:
            for a in arms:
                tst[a].append(None)
            continue
        fw = {i: 1 for i in items if fold[i] != f}
        for a, (pa, cell, gcell) in arms.items():
            counts = []
            for t in c["taus"]:
                pick, _b = _o_pol(pa, cell, fw, K, mu, t)
                counts.append(sum(gk[g][mu[pick(gcell[g])]] for g in gitems))
            ts = c["taus"][counts.index(max(counts))]
            tst[a].append(ts)
            for leg, t in (("F", 0), ("B", ts), ("B200", c["tau_fixed"])):
                pick, best = _o_pol(pa, cell, fw, K, mu, t)
                for i in ho:
                    col[(a, leg)][i] = K[i][mu[pick(cell[i])]]
            for i in ho:
                col[("BEST", "F")][i] = K[i][mu[best]]
        for a, (pa, cell) in kws.items():
            pick, _b = _o_pol(pa, cell, fw, K, mu, 0)
            for i in ho:
                col[(a, "F")][i] = K[i][mu[pick(cell[i])]]
    ucomp = sorted(set(comp.values()))
    C = len(ucomp)
    cpos = {u: j for j, u in enumerate(ucomp)}
    rng = np.random.default_rng(c["cv_seed"])
    nsd = len(c["kseeds"])
    subsets = {"ALL": items, "NO_XSRC": [i for i in items if own[i]]}

    def acc_of(key, its, cw):
        num = sum(cw[cpos[comp[i]]] * col[key][i] for i in its)
        den = sum(cw[cpos[comp[i]]] for i in its)
        return num / den

    def contr(its, cw, sd, lb):
        tb, tf = acc_of(("AF", lb), its, cw), acc_of(("AF", "F"), its, cw)
        kb = [acc_of(("BC%d" % s, lb), its, cw) for s in c["kseeds"]]
        kf = [acc_of(("BC%d" % s, "F"), its, cw) for s in c["kseeds"]]
        return tb - np.mean([kb[j] for j in sd]), (tb - tf) - np.mean([kb[j] - kf[j] for j in sd])
    reps = {(nm, lb): ([], []) for nm in subsets for lb in ("B", "B200")}
    for _b in range(c["B_cv"]):
        draws = rng.integers(0, C, C)
        sd = list(rng.integers(0, nsd, nsd))
        cw = [0] * C
        for d_ in draws:
            cw[int(d_)] += 1
        for nm, its in subsets.items():
            for lb in ("B", "B200"):
                fv, gv = contr(its, cw, sd, lb)
                reps[(nm, lb)][0].append(fv)
                reps[(nm, lb)][1].append(gv)
    one = [1] * C
    out = dict(n=len(items), comp=C, levels=levels, tstar=dict(tst), n_xsrc=sum(1 for i in items if not own[i]))
    for nm, its in subsets.items():
        for lb in ("B", "B200"):
            fv, gv = contr(its, one, list(range(nsd)), lb)
            out[(nm, lb)] = (_o_iv(fv, reps[(nm, lb)][0]), _o_iv(gv, reps[(nm, lb)][1]))
    out["acc"] = {k: float(np.mean([v[i] for i in items])) for k, v in col.items()}
    w = dict(HB1=_o_hb1(out[("ALL", "B")][0]), HB2=_o_hb2(out[("ALL", "B")][1]), HB1_TAU=_o_hb1(out[("ALL", "B200")][0]),
             HB2_TAU=_o_hb2(out[("ALL", "B200")][1]), HB1_X=_o_hb1(out[("NO_XSRC", "B")][0]), HB2_X=_o_hb2(out[("NO_XSRC", "B")][1]))
    dt = (w["HB1_TAU"], w["HB2_TAU"]) != (w["HB1"], w["HB2"])
    dx = (w["HB1_X"], w["HB2_X"]) != (w["HB1"], w["HB2"])
    w["R1"] = "FRAGILE-BOTH" if (dt and dx) else ("FRAGILE-TAU" if dt else ("FRAGILE-XSRC" if dx else "ROBUST"))
    out["words"] = w
    # HB3: full-TRAIN policies on G14's TRAIN positions; EVAL point; SE by a replay of run_boot's unit draws
    D = res["D"]
    trI = [D.items[k] for k in D.T]
    evI = [D.items[k] for k in D.E]
    allI = trI + evI
    cellE = {"AF": {i: af[i] for i in allI}}
    for s in c["kseeds"]:
        cents, bpar, _lev = _o_bc(par, Xt, tsrc, fx.reg["sources"], single_cells, s, [af[i] for i in titems if i in af])
        cellE["BC%d" % s] = {i: (af[i] if af[i] in PSEUDO else _o_file(cents, fx.vec[i])) for i in allI}
        cellE["BC%d" % s + "_par"] = bpar
        cellE["BC%d" % s + "_g"] = {g: _o_file(cents, fx.vec[g]) for g in gitems}
    parE = {"AF": par}
    gE = {"AF": {g: lay.gate_cells[g] for g in gitems}}
    for s in c["kseeds"]:
        parE["BC%d" % s] = cellE.pop("BC%d" % s + "_par")
        gE["BC%d" % s] = cellE.pop("BC%d" % s + "_g")
    w1 = {i: 1 for i in trI}
    tauE = {}
    for a in parE:
        counts = []
        for t in c["taus"]:
            pick, _b = _o_pol(parE[a], cellE[a], w1, K, mu, t)
            counts.append(sum(gk[g][mu[pick(gE[a][g])]] for g in gitems))
        tauE[a] = c["taus"][counts.index(max(counts))]

    def eval_d(wt, vv):
        acc = {}
        for a in parE:
            for leg, t in (("F", 0), ("B", tauE[a])):
                pick, _b = _o_pol(parE[a], cellE[a], wt, K, mu, t)
                acc[(a, leg)] = sum(vv[i] * K[i][mu[pick(cellE[a][i])]] for i in evI) / sum(vv[i] for i in evI)
        return acc[("AF", "B")] - np.mean([acc[("BC%d" % s, "B")] for s in c["kseeds"]]), acc
    d0, acc0 = eval_d(w1, {i: 1.0 for i in evI})
    rng = np.random.default_rng(c["seed"])
    rep = []
    for _b in range(c["B"]):
        wt = np.zeros(D.n, dtype=np.int64)
        wt[D.T] = V.draw_units(rng, D.train_units)
        v = V.draw_units(rng, D.eval_units)
        rep.append(eval_d({D.items[k]: int(wt[k]) for k in D.T}, {D.items[k]: float(v[j]) for j, k in enumerate(D.E)})[0])
    out["hb3"] = dict(point=d0, se=float(np.std(rep, ddof=1)), tau=tauE, acc=acc0)
    return out


# ── fixture layout ──────────────────────────────────────────────────────────────────────────────────────────────────────
def _fx_counts(lay):
    """The fixture's TRAIN-CV denominators by loops (so a tool that changes the scored set is refused, never re-pinned)."""
    mu, K, _man, af, _par, tr = TB._o_af(lay)
    items = [i for i in tr if af[i] not in PSEUDO and i in lay.fx.vec]
    return len(items), len({lay.fx.side[i][0] for i in items})


def build_base(tmp):
    lay = TB.build_base(tmp)
    lay.n_cv, lay.comp_cv = _fx_counts(lay)
    return lay


def clone(lay, dest):
    new = TB.clone(lay, dest)
    new.n_cv, new.comp_cv = lay.n_cv, lay.comp_cv
    return new


FX_OVER = dict(B_cv=120)


def _cap(fn, lay, **over):
    o = dict(FX_OVER, n_cv=lay.n_cv, comp_cv=lay.comp_cv)
    o.update(over)
    return U.cap(_me(), fn, lay, **o)


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "hfb", "outcome.txt")), "an outcome was written by a refusal"


def st_run_e2e(base, mk):
    lay = clone(base, mk())
    text, err, res = _cap(run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "hfb", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (HIER-FAIR-BACKOFF; --run" % U.POOL)
    c = dict(reg(), **dict(lay.common, **dict(FX_OVER, n_cv=lay.n_cv, comp_cv=lay.comp_cv)))
    with UAR._patched(lay.fx):
        o = _oracle(lay, res, c)
    af_levels = level_counts(res["P"]["H_af"])
    assert af_levels == [3, 3, 4], af_levels                          # by design: MMLU_PRO root / MATH root / BBH cell; mA, mB, MATH L0; 4 leaves
    assert all(o["levels"][s] == af_levels for s in c["kseeds"]), o["levels"]
    need(out, "per-level node counts [3, 3, 4] (= AF-U's, every seed)")
    assert (o["n"], o["comp"]) == (lay.n_cv, lay.comp_cv)
    need(out, "DENOMINATOR (Support (a)): %d TRAIN-CV items in %d CK-CLOSE components" % (o["n"], o["comp"]))
    for lab, key, ninety in (("D_final = acc(TB) - mean_s acc(BCB_s) = ", ("ALL", "B", 0), True),
                             ("D_gain = [acc(TB) - acc(TF)] - mean_s [acc(BCB_s) - acc(BCF_s)] = ", ("ALL", "B", 1), False)):
        d = o[key[:2]][key[2]]
        pat = re.escape(lab) + r"\S+ \[\S+, \S+\] \(([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]\)"
        if ninety:
            pat += r" \| 90% \[([+-][0-9.]+), ([+-][0-9.]+)\]"
        got = U.num(out, pat)
        want = [d["point"], d["lo"], d["hi"]] + ([d["lo90"], d["hi90"]] if ninety else [])
        assert all(abs(a - b_) < 6e-6 for a, b_ in zip(got, want)), (lab, got, want)
    se, = U.num(out, r"support D_final: n \d+ in \d+ components, SE ([0-9.]+) ")
    assert abs(se - o[("ALL", "B")][0]["se"]) < 6e-6, (se, o[("ALL", "B")][0]["se"])
    w = o["words"]
    need(out, "  HB1 -> %s (" % w["HB1"], "  HB2 -> %s\n" % w["HB2"], "R1 (DECIDING): %s (reference (HB1, HB2) = (%s, %s); TAU200 (%s, %s);"
         " NO-XSRC (%s, %s))" % (w["R1"], w["HB1"], w["HB2"], w["HB1_TAU"], w["HB2_TAU"], w["HB1_X"], w["HB2_X"]))
    assert res["st"]["words"]["HB1"] == w["HB1"] and res["st"]["words"]["R1"] == w["R1"]
    need(out, "TAU (GATE, per fold): tau*(AF-U) %s (median" % " ".join(str(t) for t in o["tstar"]["AF"]))
    for s in c["kseeds"]:
        need(out, "s%d %s" % (s, " ".join(str(t) for t in o["tstar"]["BC%d" % s])))
    for lab, key in (("TAU200 (tau 200 for TB and BCB in every fold and seed): D_final ", ("ALL", "B200")),
                     ("D_final ", ("NO_XSRC", "B"))):
        d = o[key][0]
        pat = re.escape(lab) + r"\S+ \[\S+, \S+\] \(([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]\) \| 90% \[([+-][0-9.]+), ([+-][0-9.]+)\]"
        if key[0] == "NO_XSRC":
            pat = r"NO-XSRC \(scored on the \d+ items .*?" + pat
        got = U.num(out, pat)
        want = [d["point"], d["lo"], d["hi"], d["lo90"], d["hi90"]]
        assert all(abs(a - b_) < 6e-6 for a, b_ in zip(got, want)), (lab, got, want)
    need(out, "%d cross-source filings removed" % o["n_xsrc"])
    for k, lab in ((("AF", "F"), "TF"), (("AF", "B"), "TB"), (("BEST", "F"), "BEST")):
        x, = U.num(out, r"ARMS \(TRAIN-CV accuracy\):.*?\b%s ([0-9.]+)" % lab)
        assert abs(x - o["acc"][k]) < 6e-6, (lab, x, o["acc"][k])
    kw, = U.num(out, r"\| KWF_s ([0-9.]+) /")
    assert abs(kw - o["acc"][("KW0", "F")]) < 6e-6, (kw, o["acc"][("KW0", "F")])
    h = o["hb3"]
    p3, lo3, hi3 = U.num(out, r"HB3 D_final = \S+ \[\S+, \S+\] \(([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]\)")
    se3, = U.num(out, r"HB3 D_final = .*?SE ([0-9.]+),")
    assert abs(p3 - h["point"]) < 6e-6 and abs(se3 - h["se"]) < 6e-6, (p3, se3, h)
    assert abs(lo3 - (h["point"] - 1.96 * h["se"])) < 2e-5 and abs(hi3 - (h["point"] + 1.96 * h["se"])) < 2e-5
    need(out, "tau* on GATE per arm: AF-U %s | BC_s %s" % (h["tau"]["AF"], " / ".join(str(h["tau"]["BC%d" % s]) for s in c["kseeds"])))
    sw = "TREE-BETTER" if lo3 > 0 else ("KMEANS-BETTER" if hi3 < 0 else "NEITHER")
    need(out, "-> %s (descriptive)" % sw, "IDENTITY: %s -> REPRODUCED" % U.identity_text(lay.common["identity"]), PILOT_SEEN, WNS, WNS_BR)
    assert out.index("IDENTITY:") < out.index("=== HIER-FAIR-BACKOFF HB1"), "a new number printed before the identity"
    assert text.index("TRAIN-CV computed BEFORE the eval view opened") < text.index("--- EVAL (eval_view"), "TRAIN-CV after the eval view"
    need(out, FHB_FIRES if w["HB1"] == "KMEANS-BETTER" else "FALSIFIER F-HB: NOT FIRED (HB1 %s;" % w["HB1"])
    need(out, (FBR_FIRES % w["R1"]) if w["R1"] in ("FRAGILE-XSRC", "FRAGILE-BOTH") else "FALSIFIER F-BR: NOT FIRED (R1 %s;" % w["R1"])
    t2, err2, _r = _cap(run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


def _syn_iv(pt, lo, hi, lo90=None, hi90=None):
    lo90 = lo if lo90 is None else lo90
    hi90 = hi if hi90 is None else hi90
    return dict(point=pt, lo=lo, hi=hi, lo90=lo90, hi90=hi90, se=0.002, se_comp=0.0015, deff=1.7, n_eff=6000.0, mde=0.0056)


def _syn_st(final, gain, tfinal=None, tgain=None, xfinal=None, xgain=None, tstar=(100,) * 10):
    acc = {("BEST", "F"): 0.6, ("AF", "F"): 0.61, ("AF", "B"): 0.62, ("AF", "B200"): 0.615}
    for s in range(5):
        acc[("BC%d" % s, "F")], acc[("BC%d" % s, "B")], acc[("BC%d" % s, "B200")], acc[("KW%d" % s, "F")] = 0.615, 0.62, 0.62, 0.61
    leg = lambda f, g: dict(final=f, gain=g, per_seed=[f["point"]] * 5)
    boot = {"ALL": dict(n=100, comp=90, acc=acc, REF=leg(final, gain), TAU200=leg(tfinal or final, tgain or gain)),
            "NO_XSRC": dict(n=95, comp=86, acc=acc, REF=leg(xfinal or final, xgain or gain), TAU200=leg(final, gain)),
            "SRC:BBH": dict(n=50, comp=45, acc=acc, REF=leg(final, gain), TAU200=leg(final, gain))}
    st = dict(n=100, comp=90, kish=1.1, fold_sizes=[10] * 10, n_gate=20, shape=[3, 3, 4], kwf_cells=[6] * 5, nseeds=5,
              tstar={"AF": list(tstar), **{"BC%d" % s: [50] * 10 for s in range(5)}}, boot=boot, n_xsrc=5, xsrc_fold=[1] * 5 + [0] * 5,
              bc_info=[dict(degenerate=0, empty=1)] * 5)
    st["words"] = words_of(st, REG)
    return st


def st_branches():
    P = REG["parity"]
    cases = ((_syn_iv(0.01, 1e-9, 0.02), "TREE-BETTER"), (_syn_iv(0.01, 0.0, 0.02, -0.001, 0.0059), "PARITY"),
             (_syn_iv(-0.01, -0.02, -1e-9), "KMEANS-BETTER"), (_syn_iv(-0.01, -0.02, 0.0, -0.006, 0.006), "PARITY"),
             (_syn_iv(0.0, -0.01, 0.01, -0.00601, 0.005), "NEITHER"), (_syn_iv(0.0, -0.01, 0.01, -0.005, 0.00601), "NEITHER"),
             (_syn_iv(0.003, 0.0005, 0.0055, 0.001, 0.005), "TREE-BETTER"), (_syn_iv(-0.003, -0.0055, -0.0005, -0.005, -0.001), "KMEANS-BETTER"))
    for d, want in cases:
        assert hb1_word(d, P) == want, (d, want, hb1_word(d, P))
    assert hb2_word(_syn_iv(0.01, 1e-9, 0.02)) == "DIVIDEND-TREE" and hb2_word(_syn_iv(0.01, 0.0, 0.02)) == "NEITHER"
    assert hb2_word(_syn_iv(-0.01, -0.02, -1e-9)) == "DIVIDEND-KMEANS" and hb2_word(_syn_iv(-0.01, -0.02, 0.0)) == "NEITHER"
    assert sign_word(_syn_iv(0.0, -0.01, 0.0059, -0.001, 0.001)) == "NEITHER"
    assert sign_word(_syn_iv(0.002, -0.001, 0.005, 0.001, 0.004)) == "NEITHER" and sign_word(_syn_iv(-0.002, -0.005, 0.001, -0.004, -0.001)) == "NEITHER"
    assert sign_word(_syn_iv(0.002, 1e-9, 0.005)) == "TREE-BETTER" and sign_word(_syn_iv(-0.002, -0.005, -1e-9)) == "KMEANS-BETTER"
    assert r1_word(("A", "B"), ("A", "B"), ("A", "B")) == "ROBUST" and r1_word(("A", "B"), ("A", "C"), ("A", "B")) == "FRAGILE-TAU"
    assert r1_word(("A", "B"), ("A", "B"), ("C", "B")) == "FRAGILE-XSRC" and r1_word(("A", "B"), ("C", "B"), ("A", "C")) == "FRAGILE-BOTH"
    # every printed branch through cv_lines (the outcome prints them verbatim)
    par_ = _syn_iv(-0.0005, -0.004, 0.003, -0.0035, 0.0025)
    dg = _syn_iv(0.005, 0.001, 0.009)
    st = _syn_st(par_, dg, tfinal=_syn_iv(-0.0045, -0.0074, -0.0016), tgain=_syn_iv(0.0012, -0.002, 0.005))
    t = "\n".join(cv_lines(st, REG))
    need(t, "  HB1 -> PARITY (neither sign word; the 90% interval [-0.00350, +0.00250] lies inside [-0.0060, +0.0060])",
         "  HB2 -> DIVIDEND-TREE", "WORDS FIXED NOW (registered)", "RULE 8: PARITY is not refuted", "RULE 8: TREE-BETTER is REFUTED (95% lower"
         " bound -0.00400 <= 0)", "RULE 8: DIVIDEND-TREE is not refuted (95% lower bound +0.00100 > 0)", "FALSIFIER F-HB: NOT FIRED (HB1 PARITY;",
         "R1 (DECIDING): FRAGILE-TAU (reference (HB1, HB2) = (PARITY, DIVIDEND-TREE); TAU200 (KMEANS-BETTER, NEITHER); NO-XSRC (PARITY,"
         " DIVIDEND-TREE))", "RULE 8 (BACKOFF-ROBUST): ROBUST is REFUTED (a word changed: FRAGILE-TAU)",
         "FALSIFIER F-BR: NOT FIRED (R1 FRAGILE-TAU; F-BR fires iff FRAGILE-XSRC or FRAGILE-BOTH); HIER-FAIR-BACKOFF's words are quoted 'at the"
         " GATE-chosen tau only'", "PREDICTION P1 D_final -0.05pp [-0.40, +0.30]: observed -0.00050 -> HELD",
         "PREDICTION P3 D_gain +0.50pp [+0.10, +0.90]: observed +0.00500 -> HELD",
         "PREDICTION P2 HB1 PARITY 0.70, NEITHER 0.20, KMEANS-BETTER 0.07, TREE-BETTER 0.03: observed PARITY; Brier 0.1358",
         "PREDICTION P4 HB2 DIVIDEND-TREE 0.80, NEITHER 0.20, DIVIDEND-KMEANS 0.00: observed DIVIDEND-TREE; Brier 0.0800",
         "PREDICTION P6 median over folds of tau*(AF-U) in [50, 200]: observed 100 -> HELD",
         "PREDICTION (BACKOFF-ROBUST) P1 TAU200 D_final -0.45pp [-0.80, -0.10]: observed -0.00450 -> HELD",
         "PREDICTION (BACKOFF-ROBUST) P1 HB1 under TAU200 KMEANS-BETTER 0.60, NEITHER 0.30, PARITY 0.10: observed KMEANS-BETTER; Brier 0.2600",
         "PREDICTION (BACKOFF-ROBUST) P2 NO-XSRC HB1 word equal to the reference (probability 0.80): PARITY vs PARITY -> TRUE; Brier 0.0400",
         "PREDICTION (BACKOFF-ROBUST) P3 R1 FRAGILE-TAU 0.55, ROBUST 0.30, FRAGILE-BOTH 0.10, FRAGILE-XSRC 0.05: observed FRAGILE-TAU; Brier 0.3050")
    st = _syn_st(_syn_iv(-0.006, -0.009, -0.003), _syn_iv(-0.004, -0.008, -0.0001), xfinal=_syn_iv(0.004, 0.001, 0.009),
                 xgain=_syn_iv(0.001, -0.002, 0.004), tstar=(50, 200, 1000, 0, None, 5, 50, 200, 200, 500))
    t = "\n".join(cv_lines(st, REG))
    need(t, "  HB1 -> KMEANS-BETTER (the 95% upper bound -0.00300 < 0)", "  HB2 -> DIVIDEND-KMEANS", FHB_FIRES,
         "RULE 8: PARITY is REFUTED (HB1 KMEANS-BETTER: a sign word)", "RULE 8: DIVIDEND-TREE is REFUTED",
         "R1 (DECIDING): FRAGILE-XSRC", FBR_FIRES % "FRAGILE-XSRC", "PREDICTION P1 D_final -0.05pp [-0.40, +0.30]: observed -0.00600 -> FAILED",
         "PREDICTION P6 median over folds of tau*(AF-U) in [50, 200]: observed 200 -> HELD",
         "PREDICTION P2 HB1 PARITY 0.70, NEITHER 0.20, KMEANS-BETTER 0.07, TREE-BETTER 0.03: observed KMEANS-BETTER; Brier 1.3958",
         "PREDICTION P4 HB2 DIVIDEND-TREE 0.80, NEITHER 0.20, DIVIDEND-KMEANS 0.00: observed DIVIDEND-KMEANS; Brier 1.6800",
         "-> FALSE; Brier 0.6400")
    st = _syn_st(_syn_iv(0.007, 0.0001, 0.012), _syn_iv(0.0, -0.002, 0.002), tfinal=_syn_iv(0.0, -0.01, 0.01, -0.007, 0.007),
                 xfinal=_syn_iv(0.0, -0.01, 0.01, -0.007, 0.007), tstar=(0, 0, 5, 20))
    t = "\n".join(cv_lines(st, REG))
    need(t, "  HB1 -> TREE-BETTER (the 95% lower bound +0.00010 > 0)", "  HB2 -> NEITHER", "RULE 8: TREE-BETTER is not refuted",
         "RULE 8: PARITY is REFUTED (HB1 TREE-BETTER: a sign word)", "R1 (DECIDING): FRAGILE-BOTH", FBR_FIRES % "FRAGILE-BOTH",
         "PREDICTION P6 median over folds of tau*(AF-U) in [50, 200]: observed 2.5 -> FAILED",
         "PREDICTION P1 D_final -0.05pp [-0.40, +0.30]: observed +0.00700 -> FAILED")
    st = _syn_st(_syn_iv(0.001, 0.0, 0.002, 0.0002, 0.0018), _syn_iv(0.004, 0.001, 0.007), tgain=_syn_iv(0.002, -0.001, 0.005))
    t = NL.join(cv_lines(st, REG))
    need(t, "  HB1 -> PARITY (", "RULE 8: TREE-BETTER is REFUTED (95% lower bound +0.00000 <= 0)",
         "R1 (DECIDING): FRAGILE-TAU (reference (HB1, HB2) = (PARITY, DIVIDEND-TREE); TAU200 (PARITY, NEITHER); NO-XSRC (PARITY, DIVIDEND-TREE))")
    st = _syn_st(_syn_iv(0.0, -0.007, 0.007, -0.0061, 0.006), _syn_iv(0.0, -0.002, 0.002), tstar=(200, 50))
    t = "\n".join(cv_lines(st, REG))
    need(t, "  HB1 -> NEITHER (neither sign word; the 90% interval [-0.00610, +0.00600] leaves [-0.0060, +0.0060])",
         "RULE 8: PARITY is REFUTED (HB1 NEITHER: the 90% interval leaves +/-0.60pp)", "R1 (DECIDING): ROBUST",
         "RULE 8 (BACKOFF-ROBUST): ROBUST is not refuted", "FALSIFIER F-BR: NOT FIRED (R1 ROBUST;",
         "PREDICTION P6 median over folds of tau*(AF-U) in [50, 200]: observed 125 -> HELD",
         "PREDICTION P1 D_final -0.05pp [-0.40, +0.30]: observed +0.00000 -> HELD",
         "PREDICTION P2 HB1 PARITY 0.70, NEITHER 0.20, KMEANS-BETTER 0.07, TREE-BETTER 0.03: observed NEITHER; Brier 1.1358")
    for d3, want in ((dict(_syn_iv(0.02, 1e-9, 0.04), se2=0.01), "TREE-BETTER"), (dict(_syn_iv(-0.02, -0.04, -1e-9), se2=0.01), "KMEANS-BETTER"),
                     (dict(_syn_iv(0.0, -0.01, 0.01), se2=0.01), "NEITHER")):
        h3 = dict(n=10, comp=9, tstar={"AF": 5, **{"K%d" % s: 5 for s in range(5)}}, acc=dict(TF=0.6, TB=0.61, BEST=0.59), bcf=[0.6] * 5,
                  bcb=[0.6] * 5, final=d3, gain=d3, final_nx=d3, n_xsrc=3)
        t = "\n".join(hb3_lines(h3, dict(REG)))
        need(t, "-> %s (descriptive)" % want)
    need(t, "PREDICTION P5 (HB3) D_final -0.30pp [-1.30, +0.70]: observed +0.00000 -> HELD")
    h3["final"] = dict(_syn_iv(-0.013, -0.04, 0.0), se2=0.01)
    need("\n".join(hb3_lines(h3, dict(REG))), "observed -0.01300 -> HELD")
    h3["final"] = dict(_syn_iv(0.0071, -0.04, 0.04), se2=0.01)
    need("\n".join(hb3_lines(h3, dict(REG))), "observed +0.00710 -> FAILED")
    assert median_tau([None, 5, 200, 50]) == 50.0 and median_tau([0, 5]) == 2.5 and median_tau([None]) != median_tau([None])


def st_cv_unit():
    """cv_predict / cv_boot on a hand-sized planted problem against the loop oracle (_o_pol, own fold scoring, own replay)."""
    rng = np.random.default_rng(3)
    mu = ["m0", "m1", "m2"]
    par = {UNION: None, "S:r": UNION, "S:a": "S:r", "S:b": "S:r", "S:a1": "S:a", "S:a2": "S:a", "S:b1": "S:b", "S:b2": "S:b"}
    par2 = {UNION: None, "T:r": UNION, "T:x": "T:r", "T:y": "T:r", "T:x1": "T:x", "T:x2": "T:x", "T:y1": "T:y", "T:y2": "T:y"}
    leaves1, leaves2 = ["S:a1", "S:a2", "S:b1", "S:b2"], ["T:x1", "T:x2", "T:y1", "T:y2"]
    n = 160
    items = ["i%03d" % j for j in range(n)]
    cell1 = {i: leaves1[j % 4] for j, i in enumerate(items)}
    cell2 = {i: leaves2[(j // 3) % 4] for j, i in enumerate(items)}
    K = {i: {m_: int(rng.random() < (0.3 + 0.4 * (leaves1.index(cell1[i]) == mi))) for mi, m_ in enumerate(mu)} for i in items}
    gate = ["g%02d" % j for j in range(24)]
    gc1 = {g: leaves1[j % 4] for j, g in enumerate(gate)}
    gc2 = {g: leaves2[j % 4] for j, g in enumerate(gate)}
    Kg = {g: {m_: int(rng.random() < 0.5) for m_ in mu} for g in gate}
    comp = ["c%02d" % (j // 2) for j in range(n)]
    fold = np.array([int(hashlib.sha256((x + "SALT").encode()).hexdigest(), 16) % 4 for x in comp])

    def hier(p):
        names = list(p)
        return TB.Hier("h", names, [p[x] for x in names], set(x for x in names if x not in set(p.values())))
    h1, h2 = hier(par), hier(par2)
    A = np.array([[K[i][m_] for m_ in mu] for i in items], dtype=np.int64)
    KG = np.array([[Kg[g][m_] for m_ in mu] for g in gate], dtype=np.int64)
    arms = {"AF": TB.Arm("a", h1, [cell1[i] for i in items], [gc1[g] for g in gate], 3)}
    for s in range(2):
        arms["BC%d" % s] = TB.Arm("b", h2 if s == 0 else h1, [(cell2 if s == 0 else cell1)[i] for i in items],
                                  [(gc2 if s == 0 else gc1)[g] for g in gate], 3)
    kwh = flat_hier("k", leaves2)
    kw = {"KW0": TB.Arm("k", kwh, [cell2[i] for i in items], [], 3), "KW1": TB.Arm("k", kwh, [cell2[i] for i in items], [], 3)}
    taus = [0, 1, 5, 50, 200]
    cols, tst = cv_predict(A, fold, arms, kw, KG, taus, 4, 200)
    cellmaps = {"AF": (par, cell1, gc1), "BC0": (par2, cell2, gc2), "BC1": (par, cell1, gc1)}
    for f in range(4):
        fw = {i: 1 for j, i in enumerate(items) if fold[j] != f}
        ho = [j for j in range(n) if fold[j] == f]
        for a, (pa, ce, gce) in cellmaps.items():
            counts = []
            for t in taus:
                pick, _b = _o_pol(pa, ce, fw, K, mu, t)
                counts.append(sum(Kg[g][mu[pick(gce[g])]] for g in gate))
            ts = taus[counts.index(max(counts))]
            assert tst[a][f] == ts, (a, f, tst[a][f], ts, counts)
            for leg, t in (("F", 0), ("B", ts), ("B200", 200)):
                pick, best = _o_pol(pa, ce, fw, K, mu, t)
                for j in ho:
                    assert cols[(a, leg)][j] == K[items[j]][mu[pick(ce[items[j]])]], (a, leg, j)
                    assert cols[("BEST", "F")][j] == K[items[j]][mu[best]]
        kpar = {UNION: None, **{x: UNION for x in leaves2}}
        pick, _b = _o_pol(kpar, cell2, fw, K, mu, 0)
        for j in ho:
            assert cols[("KW0", "F")][j] == K[items[j]][mu[pick(cell2[items[j]])]]
    own = np.array([j % 5 != 0 for j in range(n)])
    out = cv_boot(cols, comp, [("ALL", np.ones(n, bool)), ("NO_XSRC", own)], 50, 9, 2)
    uc = sorted(set(comp))
    rng2 = np.random.default_rng(9)
    for b in range(50):
        draws = rng2.integers(0, len(uc), len(uc))
        sd = rng2.integers(0, 2, 2)
        if b == 49:
            cw = Counter(int(x) for x in draws)
            for nm, mk in (("ALL", np.ones(n, bool)), ("NO_XSRC", own)):
                def acc(key):
                    num = sum(cw[uc.index(comp[j])] * cols[key][j] for j in range(n) if mk[j])
                    return num / sum(cw[uc.index(comp[j])] for j in range(n) if mk[j])
                kb = [acc(("BC%d" % s, "B")) for s in range(2)]
                kf = [acc(("BC%d" % s, "F")) for s in range(2)]
                f_ = acc(("AF", "B")) - np.mean([kb[x] for x in sd])
                g_ = (acc(("AF", "B")) - acc(("AF", "F"))) - np.mean([kb[x] - kf[x] for x in sd])
                fc = acc(("AF", "B")) - np.mean(kb)
                assert abs(out[nm]["REF"]["final"]["point"] - (np.mean(cols[("AF", "B")][mk]) - np.mean([np.mean(cols[("BC%d" % s, "B")][mk]) for s in range(2)]))) < 1e-12
                del f_, g_, fc
    # whole-distribution replay of ALL / REF
    rng3 = np.random.default_rng(9)
    reps, repc = [], []
    for b in range(50):
        draws = rng3.integers(0, len(uc), len(uc))
        sd = rng3.integers(0, 2, 2)
        cw = Counter(int(x) for x in draws)
        def acc(key):
            return sum(cw[uc.index(comp[j])] * cols[key][j] for j in range(n)) / sum(cw[uc.index(comp[j])] for j in range(n))
        kb = [acc(("BC%d" % s, "B")) for s in range(2)]
        reps.append(acc(("AF", "B")) - np.mean([kb[x] for x in sd]))
        repc.append(acc(("AF", "B")) - np.mean(kb))
    d = out["ALL"]["REF"]["final"]
    assert abs(d["lo"] - np.percentile(reps, 2.5)) < 1e-12 and abs(d["hi90"] - np.percentile(reps, 95)) < 1e-12, (d, np.percentile(reps, 2.5))
    assert abs(d["se"] - np.std(reps, ddof=1)) < 1e-12 and abs(d["se_comp"] - np.std(repc, ddof=1)) < 1e-12
    assert abs(d["deff"] - np.var(reps, ddof=1) / np.var(repc, ddof=1)) < 1e-9 and abs(d["n_eff"] - len(uc) / d["deff"]) < 1e-6


def st_train_cv_unit():
    """train_cv() itself on a hand-made world with cross-source filings and a pseudo-leaf item: the scored set, NO_XSRC (own = the
    AF leaf's member equals the stratum source), its count per fold, the subsets, the folds by sha256, D_final on NO_XSRC by loops."""
    rng = np.random.default_rng(5)
    mu = ["m0", "m1", "m2"]
    names = [UNION, "S:r", "S:a", "S:b", "T:r", "T:c", "T:d"] + list(PSEUDO)
    par = {UNION: None, "S:r": UNION, "S:a": "S:r", "S:b": "S:r", "T:r": UNION, "T:c": "T:r", "T:d": "T:r"}
    par.update({p_: UNION for p_ in PSEUDO})
    lv = {"S:a", "S:b", "T:c", "T:d"} | set(PSEUDO)
    H = TB.Hier("AF-U", names, [par[x] for x in names], lv)
    Hb = {s_: TB.Hier("BC%d" % s_, [("BC%d|" % s_ + x) if x not in PSEUDO and x != UNION else x for x in names],
                      [None if par[x] is None else (("BC%d|" % s_ + par[x]) if par[x] not in PSEUDO and par[x] != UNION else par[x]) for x in names],
                      set(("BC%d|" % s_ + x) if x not in PSEUDO else x for x in lv)) for s_ in range(5)}
    cents = {"S:a": [1, 0, 0, 0], "S:b": [0, 1, 0, 0], "T:c": [0, 0, 1, 0], "T:d": [0, 0, 0, 1]}
    items, meta, K, af, vec = [], {}, {}, {}, {}
    for j in range(130):
        i = "it%03d" % j
        so = "S" if j % 2 == 0 else "T"
        own_leaf = ("S:a" if j % 4 == 0 else "S:b") if so == "S" else ("T:c" if j % 4 == 1 else "T:d")
        leaf = own_leaf if j % 7 else ("T:c" if so == "S" else "S:a")         # every 7th item filed into the other source
        if j == 5:
            leaf = PSEUDO[1]                                                  # an <unrouted> item: never scored
        items.append(i)
        af[i] = leaf
        meta[i] = ("c%02d" % (j // 3), so, so + "/d")
        K[i] = {m_: int(rng.random() < 0.5) for m_ in mu}
        vec[i] = np.array(cents.get(leaf, [0.5, 0.5, 0.5, 0.5]), dtype=float) + 0.1 * rng.normal(size=4)
    gitems = ["g%02d" % j for j in range(12)]
    gk = {g: {m_: int(rng.random() < 0.5) for m_ in mu} for g in gitems}
    for j, g in enumerate(gitems):
        vec[g] = np.array(list(cents.values())[j % 4], dtype=float)
    gcell = {g: list(cents)[j % 4] for j, g in enumerate(gitems)}

    def mkfile(s_):
        C = np.array(list(cents.values()), dtype=float)
        return filer(C, ["BC%d|" % s_ + x for x in cents])
    P_ = dict(af=af, vec=vec, H_af=H, gcell=gcell, H_bc=Hb, bc_file={s_: mkfile(s_) for s_ in range(5)},
              kx={"K%d" % s_: {i: "K%d:%s:000" % (s_, meta[i][1]) for i in items} for s_ in range(5)}, shape=[2, 4], bc_info=[{}] * 5)
    scored = [i for i in items if af[i] not in PSEUDO]
    c = dict(REG, n_cv=len(scored), comp_cv=len({meta[i][0] for i in scored}), B_cv=40)
    st = train_cv(P_, K, meta, mu, gk, gitems, c, lambda s_: None)
    own = {i: af[i].split(":")[0] == meta[i][1] for i in scored}
    fold = {i: int(hashlib.sha256((meta[i][0] + c["fold_salt"]).encode("utf-8")).hexdigest(), 16) % 10 for i in scored}
    nx = sum(1 for i in scored if not own[i])
    assert nx >= 15 and st["n_xsrc"] == nx and st["items"] == sorted(scored), (st["n_xsrc"], nx)
    assert st["xsrc_fold"] == [sum(1 for i in scored if fold[i] == f and not own[i]) for f in range(10)], st["xsrc_fold"]
    assert st["fold_sizes"] == [sum(1 for i in scored if fold[i] == f) for f in range(10)]
    b = st["boot"]
    assert b["NO_XSRC"]["n"] == len(scored) - nx and b["SRC:S"]["n"] == sum(1 for i in scored if meta[i][1] == "S")
    assert b["NON_BBH"]["n"] == len(scored) and b["ALL"]["n"] == len(scored)
    pos = {i: j for j, i in enumerate(st["items"])}
    ox = [pos[i] for i in scored if own[i]]

    def mean(key, rows):
        return float(np.mean([st["cols"][key][r] for r in rows]))
    want = mean(("AF", "B"), ox) - np.mean([mean(("BC%d" % s_, "B"), ox) for s_ in range(5)])
    assert abs(b["NO_XSRC"]["REF"]["final"]["point"] - want) < 1e-12, (b["NO_XSRC"]["REF"]["final"]["point"], want)
    allr = list(range(len(scored)))
    want = mean(("AF", "B200"), allr) - np.mean([mean(("BC%d" % s_, "B200"), allr) for s_ in range(5)])
    assert abs(b["ALL"]["TAU200"]["final"]["point"] - want) < 1e-12
    for j, i in enumerate(st["items"]):
        assert st["cols"][("AF", "F")][j] in (0.0, 1.0)
    st2 = None
    try:
        train_cv(P_, K, meta, mu, gk, gitems + [scored[0]], c, lambda s_: None)
    except SystemExit as e:
        st2 = str(e)
    assert st2 and "[HFB-GATE-SIDE]" in st2, st2


def st_bc_unit():
    """bc_build on a hand tree: shape equal, matching rule (largest cluster -> the child with most leaves), single-child node,
    degenerate node, one-cell source, empty leaf; check_shape's refusal."""
    names = [UNION, "MMLU_PRO_LB:r", "MMLU_PRO_LB:p", "MMLU_PRO_LB:q", "MMLU_PRO_LB:p1", "MMLU_PRO_LB:p2", "MMLU_PRO_LB:p3", "MMLU_PRO_LB:q1", "MMLU_PRO_LB:s", "MMLU_PRO_LB:s1", "MMLU_PRO_LB:t", "MMLU_PRO_LB:t1", "MMLU_PRO_LB:t2", "B:c1"] + list(PSEUDO)
    par = {UNION: None, "MMLU_PRO_LB:r": UNION, "MMLU_PRO_LB:p": "MMLU_PRO_LB:r", "MMLU_PRO_LB:q": "MMLU_PRO_LB:r", "MMLU_PRO_LB:p1": "MMLU_PRO_LB:p", "MMLU_PRO_LB:p2": "MMLU_PRO_LB:p", "MMLU_PRO_LB:p3": "MMLU_PRO_LB:p", "MMLU_PRO_LB:q1": "MMLU_PRO_LB:q",
           "MMLU_PRO_LB:s": "MMLU_PRO_LB:r", "MMLU_PRO_LB:s1": "MMLU_PRO_LB:s", "MMLU_PRO_LB:t": "MMLU_PRO_LB:s1", "MMLU_PRO_LB:t1": "MMLU_PRO_LB:t", "MMLU_PRO_LB:t2": "MMLU_PRO_LB:t", "B:c1": UNION}
    for p in PSEUDO:
        par[p] = UNION
    leaves = {"MMLU_PRO_LB:p1", "MMLU_PRO_LB:p2", "MMLU_PRO_LB:p3", "MMLU_PRO_LB:q1", "MMLU_PRO_LB:t1", "MMLU_PRO_LB:t2", "B:c1"} | set(PSEUDO)
    H = TB.Hier("AF", names, [par[x] for x in names], leaves)
    rng = np.random.default_rng(1)
    dirs = [np.eye(6)[j] for j in range(6)]
    X, src = [], []
    for j, (cnt, d) in enumerate(((30, 0), (1, 1), (1, 2))):   # the 1-row clusters reach A:s -> A:s1 -> A:t (2 children): degenerate,
        for _ in range(cnt):                                       # one empty leaf
            X.append(dirs[d] + 0.05 * rng.normal(size=6))
            src.append("MMLU_PRO_LB")
    for _ in range(7):
        X.append(dirs[4] + 0.05 * rng.normal(size=6))
        src.append("B")
    Xt = FM.unit_rows(np.array(X))
    under = np.zeros(H.N)
    hb, C, cn, info = bc_build(H, Xt, np.array(src), ["MMLU_PRO_LB", "B"], {"B": {"cell": "B:c1"}}, 0, under)
    assert level_counts(hb) == level_counts(H) == [2, 3, 5, 1, 2], (level_counts(hb), level_counts(H))
    cents, bpar, lev = _o_bc(par, Xt, src, ["MMLU_PRO_LB", "B"], {"B": "B:c1"}, 0, [])
    assert lev == level_counts(H) and set(cents) == set(cn), (lev, sorted(cents), sorted(cn))
    for nm, cv in zip(cn, C):
        assert np.allclose(cents[nm], cv), nm
    assert info["degenerate"] >= 1 and info["empty"] >= 1, info
    assert check_shape(H, hb, "x") == level_counts(H)
    flat = TB.Hier("F", [UNION, "x1", "x2"] + list(PSEUDO), [None, UNION, UNION] + [UNION] * len(PSEUDO), {"x1", "x2"} | set(PSEUDO))
    try:
        check_shape(H, flat, "BCx")
        raise AssertionError("shape refusal not enforced")
    except SystemExit as e:
        assert "[HFB-SHAPE] BCx per-level node counts" in str(e)
    f = filer(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]), ["a", "b", "c"])
    assert f([1.0, 0.0]) == "a" and f([0.2, 0.9]) == "b"
    assert fold_of("c1", "S", 10) == int(hashlib.sha256(b"c1S").hexdigest(), 16) % 10


def st_refusals(base, mk):
    lay = clone(base, mk())
    saved = UAR._POOL[0]
    buf = io.StringIO()
    with U.mine(_me(), lay, **dict(FX_OVER, n_cv=lay.n_cv, comp_cv=lay.comp_cv)):
        UAR._POOL[0] = lambda pool: (1, "stub failure")
        try:
            with contextlib.redirect_stdout(buf):
                try:
                    run(out=lambda s: print(s))
                    err = None
                except SystemExit as e:
                    err = str(e)
        finally:
            UAR._POOL[0] = saved
    assert err and "B0-2 pool check failed" in err, err
    assert buf.getvalue().splitlines()[0].startswith("POOL "), "the POOL line is not first"
    _no_outcome(lay)
    for over, needle in ((dict(n_cv=lay.n_cv + 1), "[HFB-CV-DENOM]"), (dict(comp_cv=lay.comp_cv - 1), "[HFB-CV-DENOM]"),
                         (dict(n_gate_key=lay.common["n_gate_key"] + 1), "[HFB-GATE-DENOM]"), (dict(n_route=lay.common["n_route"] + 1), "[HFB-DENOM]"),
                         (dict(B=lay.common["B"] + 1), "B / seed")):
        lay = clone(base, mk())
        t_, err, _r = _cap(run, lay, **over)
        assert err and needle in err, (over, err)
        if needle in ("[HFB-CV-DENOM]", "[HFB-GATE-DENOM]"):
            assert "--- EVAL (eval_view" not in t_ and not os.path.exists(os.path.join(lay.tmp, "res", "hfb", "READ_STARTED")), \
                "the eval view opened before a TRAIN-CV refusal"
        _no_outcome(lay)
    idn = lay.common["identity"]
    lay = clone(base, mk())
    t_, err, _r = _cap(run, lay, identity=dict(idn, af=idn["af"][:-1] + str((int(idn["af"][-1]) + 1) % 10)))
    assert err and "[HFB-IDENTITY]" in err, err
    assert "=== HIER-FAIR-BACKOFF HB1" not in t_ and "HB1 ->" not in t_, "a word printed before the identity refusal"
    _no_outcome(lay)
    lay = clone(base, mk())
    g = globals()
    real = g["bc_build"]

    def bc_flat(H, Xt, tsrc, sources, single, seed, af_under, kfit=None):
        h, C, cn, info = real(H, Xt, tsrc, sources, single, seed, af_under, kfit)
        if seed == 3:
            leaves_ = [x for x in h.names if h.leaf[h.idx[x]] and x not in PSEUDO]
            names = [UNION] + leaves_ + list(PSEUDO)
            h = TB.Hier("flat", names, [None] + [UNION] * (len(names) - 1), set(names[1:]))
        return h, C, cn, info
    g["bc_build"] = bc_flat
    try:
        _t, err, _r = _cap(run, lay)
    finally:
        g["bc_build"] = real
    assert err and "[HFB-SHAPE] BC3" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    real_gi, real_gk = ERC.gate_items, EC.gate_key
    intruder = sorted(i for i, (_c, s_) in lay.fx.side.items() if s_ == "TRAIN" and i in lay.fx.filed and lay.fx.filed[i])[0]

    def gi_bad(rows_h, side):
        its, gcell, gsrc = real_gi(rows_h, side)
        return sorted(its + [intruder]), dict(gcell, **{intruder: lay.fx.filed[intruder]}), gsrc

    def gk_bad(cfg, say, models, gits):
        K, comp, want = real_gk(cfg, say, models, [g_ for g_ in gits if g_ != intruder])
        return dict(K, **{intruder: {m: 0 for m in models}}), sorted(comp + [intruder]), want
    ERC.gate_items, EC.gate_key = gi_bad, gk_bad
    try:
        _t, err, _r = _cap(run, lay, n_gate_key=lay.common["n_gate_key"] + 1)
    finally:
        ERC.gate_items, EC.gate_key = real_gi, real_gk
    assert err and "[HFB-GATE-SIDE]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    real_picks, real_rb = TB.picks, V.run_boot
    active = [False]

    def picks_bad(h, S, n, tau):
        pk, gb = real_picks(h, S, n, tau)
        if active[0] and tau == 0 and h.label == "AF-U":           # the hook's TF only (run_boot's own arms use V.fit)
            pk = pk.copy()
            v0 = [v for v in range(h.N) if h.leaf[v] and n[v] >= 1][0]
            pk[v0] = (pk[v0] + 1) % S.shape[1]
        return pk, gb

    def rb(*a, **k):
        active[0] = True
        try:
            return real_rb(*a, **k)
        finally:
            active[0] = False
    TB.picks, V.run_boot = picks_bad, rb
    try:
        _t, err, _r = _cap(run, lay)
    finally:
        TB.picks, V.run_boot = real_picks, real_rb
    assert err and "[HFB-MIRROR]" in err, err
    _no_outcome(lay)
    lay = clone(base, mk())
    os.makedirs(os.path.join(lay.tmp, "res", "hfb"), exist_ok=True)
    open(os.path.join(lay.tmp, "res", "hfb", "READ_STARTED"), "w").close()
    _t, err, _r = _cap(run, lay)
    assert err and "write-once" in err, err
    _no_outcome(lay)


def st_dry_run(base, mk):
    lay = clone(base, mk())
    text, err, _r = _cap(dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (HIER-FAIR-BACKOFF; --dry-run" % U.POOL), ls[0]
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read", "POOL CHECK (B0-2): rc 0",
         "AF-U HIERARCHY (tree_backoff R1):", "per-level node counts [3, 3, 4]", "BC4 (HB-R1):", "= AF-U's", "COST: 0 calls")
    for bad in ("HB1 ->", "D_final =", "IDENTITY:", "TAU (GATE", "PREDICTION", "GATE key (EC-R7)", "TRAIN-CV computed"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "hfb")), "the dry-run wrote under res/hfb"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (HIER-FAIR-BACKOFF; --dry-run"), L[0]
    need(t, "TRAIN-CV 11841 items in 10781 CK-CLOSE components", "DEFF 1.61 (D_final) / 1.56 (D_gain)", "PARITY margin +/-0.60pp",
         "HB3 EVAL 5907 / 5404", "10 folds (salt HIER-FAIR-BACKOFF-FOLDS-1)", "on the 1944 key-complete GATE items", "TAU200 = tau 200",
         "CV bootstrap B 2000 default_rng(20261008)", "HB3 run_boot B 2000 default_rng(42)", VERDICT_HB,
         "best single 0.6049, TRUE source 0.6150, AF-U leaf cell 0.6201, K_s K0 0.6271; C1 +2.67pp [+1.46pp, +3.89pp]; G_AF +1.52pp [+0.14pp, +2.91pp]",
         "L24974-L24987", "L24989-L25000", "calls 0")
    assert REG["out"] == "experiment_results/archv2/hier_fair_backoff/outcome.txt" and REG["uar_policy_sha"].startswith("8d68018c")
    assert REG["manifest_sha"].startswith("53021e26") and REG["B"] == 2000 and REG["n_gate_key"] == 1944 and REG["taus"] == TB.TAUS
    assert (REG["n_cv"], REG["comp_cv"], REG["nfold"], REG["B_cv"], REG["cv_seed"], REG["parity"], REG["tau_fixed"]) == (
        11841, 10781, 10, 2000, 20261008, 0.0060, 200) and tuple(REG["kseeds"]) == (0, 1, 2, 3, 4)


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("branches", "HB1 / HB2 / R1 / HB3 words at their boundaries; every cv_lines / hb3_lines branch; every Brier and band", "plain"),
         ("cv_unit", "cv_predict / cv_boot on a planted problem vs loops: tau* per fold, every column, the two-stage replay, DEFF", "plain"),
         ("train_cv", "train_cv() on a world with cross-source filings: scored set, NO_XSRC by member != stratum, per fold, subsets", "plain"),
         ("bc_unit", "bc_build on a hand tree vs the loop builder: shape, matching, single-child, degenerate, one-cell, empty leaf", "plain"),
         ("run_e2e", "--run end to end on tree_backoff's deepened fixture vs the loop oracle (TRAIN-CV words and numbers, HB3)", "base"),
         ("refusals", "pool, CV-DENOM, GATE-DENOM, DENOM, B / seed, IDENTITY, SHAPE, GATE-SIDE, MIRROR, write-once; no outcome", "base"),
         ("dry_run", "--dry-run: POOL first, structure, no statistic, nothing written; the REAL constants' lines", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"branches": st_branches, "cv_unit": st_cv_unit, "train_cv": st_train_cv_unit, "bc_unit": st_bc_unit, "run_e2e": st_run_e2e, "refusals": st_refusals,
       "dry_run": st_dry_run, "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None):
    import tempfile
    import scratch_dir   # noqa: F401  TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="hfb_")
        made.append(d)
        return os.path.join(d, "lay")
    HIT.clear()
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                if kind == "base" and base is None:
                    with contextlib.redirect_stdout(io.StringIO()):
                        base = build_base(mk())
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(base, mk)
                if not quiet:
                    print("  ok   %-13s %s" % (name, desc), flush=True)
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    import traceback
                    print("  FAIL %-13s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:600]), flush=True)
                    traceback.print_exc()
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    """tree_backoff's procedure: each mutant edits the code ABOVE the SELFTEST marker in memory, executes the edited module and runs
    its selftest on one fixture base built by the unedited code; KILLED iff the selftest fails. X00 must survive. No file written."""
    import tempfile
    import scratch_dir   # noqa: F401
    import shutil
    mark = "\n# " + chr(0x2550) * 2 + " SELFTEST"
    path = os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    cut = src.index(mark)
    d = tempfile.mkdtemp(prefix="hfb_mut_")
    rows, bad = [], []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            base = build_base(os.path.join(d, "lay"))
        for name, old, new in MUTANTS:
            if only and not any(name.startswith(o) for o in only):
                continue
            head = src[:cut]
            if old and head.count(old) != 1:
                bad.append(name)
                print("  %-74s NOT APPLIED (%d matches)" % (name, head.count(old)), flush=True)
                continue
            try:
                mod = types.ModuleType("hier_fair_backoff_mutant")
                mod.__file__ = path
                exec(compile((head.replace(old, new) if old else head) + src[cut:], path, "exec"), mod.__dict__)
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.selftest(quiet=True, base=base)
                res = "SURVIVED"
            except BaseException as e:   # noqa: B902
                res = "KILLED (%s)" % type(e).__name__
            rows.append((name, res))
            print("  %-74s %s" % (name, res), flush=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    ("X01 HB1 TREE-BETTER at lo >= 0", 'def hb1_word(d, parity):' + NL + '    if d["lo"] > 0:', 'def hb1_word(d, parity):' + NL + '    if d["lo"] >= 0:'),
    ("X02 HB1 KMEANS-BETTER at hi <= 0", '        return "TREE-BETTER"' + NL + '    if d["hi"] < 0:' + NL + '        return "KMEANS-BETTER"' + NL + '    if d["lo90"]',
     '        return "TREE-BETTER"' + NL + '    if d["hi"] <= 0:' + NL + '        return "KMEANS-BETTER"' + NL + '    if d["lo90"]'),
    ("X03 PARITY open at the margin", '    if d["lo90"] >= -parity and d["hi90"] <= parity:', '    if d["lo90"] > -parity and d["hi90"] < parity:'),
    ("X04 PARITY on the 95% interval", '    if d["lo90"] >= -parity and d["hi90"] <= parity:', '    if d["lo"] >= -parity and d["hi"] <= parity:'),
    ("X05 PARITY tested before the sign words", 'def hb1_word(d, parity):' + NL + '    if d["lo"] > 0:',
     'def hb1_word(d, parity):' + NL + '    if d["lo90"] >= -parity and d["hi90"] <= parity:' + NL + '        return "PARITY"' + NL + '    if d["lo"] > 0:'),
    ("X06 HB2 DIVIDEND-TREE at lo >= 0", 'def hb2_word(d):' + NL + '    if d["lo"] > 0:', 'def hb2_word(d):' + NL + '    if d["lo"] >= 0:'),
    ("X07 HB2 DIVIDEND-KMEANS at hi <= 0", '        return "DIVIDEND-TREE"' + NL + '    if d["hi"] < 0:', '        return "DIVIDEND-TREE"' + NL + '    if d["hi"] <= 0:'),
    ("X08 R1 tau / xsrc swapped", '    dt, dx = bool(tau != ref), bool(xsrc != ref)', '    dt, dx = bool(xsrc != ref), bool(tau != ref)'),
    ("X09 R1 compares HB1 only", '    w["R1"] = r1_word((w["HB1"], w["HB2"]), (w["HB1_TAU"], w["HB2_TAU"]), (w["HB1_X"], w["HB2_X"]))',
     '    w["R1"] = r1_word(w["HB1"], w["HB1_TAU"], w["HB1_X"])'),
    ("X10 F-BR fires on FRAGILE-TAU too", '    w["F_BR"] = bool(w["R1"] in ("FRAGILE-XSRC", "FRAGILE-BOTH"))',
     '    w["F_BR"] = bool(w["R1"] in ("FRAGILE-XSRC", "FRAGILE-BOTH", "FRAGILE-TAU"))'),
    ("X11 F-HB fires on TREE-BETTER", '    w["F_HB"] = bool(w["HB1"] == "KMEANS-BETTER")', '    w["F_HB"] = bool(w["HB1"] == "TREE-BETTER")'),
    ("X12 NO-XSRC words read on ALL", 'HB1_X=hb1_word(NX["REF"]["final"], c["parity"])', 'HB1_X=hb1_word(ALL["REF"]["final"], c["parity"])'),
    ("X13 TAU200 words read on the reference leg", 'HB1_TAU=hb1_word(ALL["TAU200"]["final"], c["parity"])',
     'HB1_TAU=hb1_word(ALL["REF"]["final"], c["parity"])'),
    ("X14 parity margin 0.50pp", 'parity=0.0060, tau_fixed=200', 'parity=0.0050, tau_fixed=200'),
    ("X15 fold hash salt first", '    return int(hashlib.sha256((str(comp) + salt).encode("utf-8")).hexdigest(), 16) % nfold',
     '    return int(hashlib.sha256((salt + str(comp)).encode("utf-8")).hexdigest(), 16) % nfold'),
    ("X16 tau ties to the larger tau", '            ts = taus[int(np.argmax(counts))]', '            ts = taus[len(taus) - 1 - int(np.argmax(counts[::-1]))]'),
    ("X17 the held-out fold enters the fit (leak)", '        w = (fold != f).astype(np.int64)', '        w = np.ones(len(fold), dtype=np.int64)'),
    ("X18 TAU200 leg at tau*", '            p2, _g = TB.picks(arm.h, S, nn, tau_fixed)', '            p2, _g = TB.picks(arm.h, S, nn, ts)'),
    ("X19 seeds not resampled", '                r["final"][b] = t_b - k_b[sd].mean()', '                r["final"][b] = t_b - k_b.mean()'),
    ("X20 seeds drawn before components", '        cnt = np.bincount(rng.integers(0, C, C), minlength=C).astype(np.float64)' + NL + '        sd = rng.integers(0, nseeds, nseeds)',
     '        sd = rng.integers(0, nseeds, nseeds)' + NL + '        cnt = np.bincount(rng.integers(0, C, C), minlength=C).astype(np.float64)'),
    ("X21 95% interval at 5 / 95", '    lo, hi = (float(np.percentile(two, 2.5)), float(np.percentile(two, 97.5))) if len(two) else (pt, pt)',
     '    lo, hi = (float(np.percentile(two, 5)), float(np.percentile(two, 95))) if len(two) else (pt, pt)'),
    ("X22 90% interval at 2.5 / 97.5", '    lo90, hi90 = (float(np.percentile(two, 5)), float(np.percentile(two, 95))) if len(two) else (pt, pt)',
     '    lo90, hi90 = (float(np.percentile(two, 2.5)), float(np.percentile(two, 97.5))) if len(two) else (pt, pt)'),
    ("X23 D_gain replicate sign", '                r["gain"][b] = (t_b - t_f) - (k_b[sd] - k_f[sd]).mean()', '                r["gain"][b] = (t_b - t_f) + (k_b[sd] - k_f[sd]).mean()'),
    ("X24 D_gain point without the k-means dividend", '                          gain=interval(float((t_b - t_f) - (k_b - k_f).mean()), r["gain"], r["gain_c"], o["comp"]),',
     '                          gain=interval(float(t_b - t_f), r["gain"], r["gain_c"], o["comp"]),'),
    ("X25 D_final point: first seed only", '            o[leg] = dict(final=interval(float(t_b - k_b.mean()), r["final"], r["final_c"], o["comp"]),',
     '            o[leg] = dict(final=interval(float(t_b - k_b[0]), r["final"], r["final_c"], o["comp"]),'),
    ("X26 SE from the component-only bootstrap", '    se = float(np.std(two, ddof=1)) if len(two) > 1 else 0.0', '    se = float(np.std(comp_only, ddof=1)) if len(two) > 1 else 0.0'),
    ("X27 n_eff on items, not components", '                n_eff=(n_units / deff) if deff == deff and deff > 0 else float("nan"), mde=2.8 * se)',
     '                n_eff=(n_units * deff) if deff == deff and deff > 0 else float("nan"), mde=2.8 * se)'),
    ("X28 pseudo-leaf items scored", '                   if i in train_meta and af.get(i) is not None and af[i] not in PSEUDO and i in vec)',
     '                   if i in train_meta and af.get(i) is not None and i in vec)'),
    ("X29 own source inverted", '    own = np.array([UCI.cell_member(af[i]) == strat[j] for j, i in enumerate(items)], dtype=bool)',
     '    own = np.array([UCI.cell_member(af[i]) != strat[j] for j, i in enumerate(items)], dtype=bool)'),
    ("X30 NO_XSRC = ALL", '    masks = [("ALL", np.ones(len(items), dtype=bool)), ("NO_XSRC", own),', '    masks = [("ALL", np.ones(len(items), dtype=bool)), ("NO_XSRC", np.ones(len(items), dtype=bool)),'),
    ("X31 CV denominators not enforced", '    if (len(items), n_c) != (c["n_cv"], c["comp_cv"]):', '    if False:'),
    ("X32 GATE / TRAIN-CV overlap not refused", '    if set(items) & set(gitems):', '    if False:'),
    ("X33 GATE denominator not enforced", '        if len(gitems) != int(c["n_gate_key"]):', '        if False:'),
    ("X34 shape not checked", '    if a != b:' + NL + '        hit("REFUSE.SHAPE")', '    if False:' + NL + '        hit("REFUSE.SHAPE")'),
    ("X35 children matched smallest leaf count first", '            ko = sorted(kids, key=lambda c: (-leafcount(c), -int(af_under[c]), H.names[c]))',
     '            ko = sorted(kids, key=lambda c: (leafcount(c), -int(af_under[c]), H.names[c]))'),
    ("X36 clusters not ordered by size", '            clus = sorted(range(bk), key=lambda j: (-int((lab == j).sum()), j))', '            clus = list(range(bk))'),
    ("X37 filing to the farthest centroid", '    return lambda x: cnames[int(np.argmax(Cn @ np.asarray(x, dtype=np.float64)))]',
     '    return lambda x: cnames[int(np.argmin(Cn @ np.asarray(x, dtype=np.float64)))]'),
    ("X38 HB3 D_final on the flat k-means columns", '    wf[TB.KB0:TB.KB0 + 5] -= 0.2' + NL + '    wg = np.zeros(TB.NCOL)',
     '    wf[TB.KF0:TB.KF0 + 5] -= 0.2' + NL + '    wg = np.zeros(TB.NCOL)'),
    ("X39 HB3 mirror not enforced", '            if a.shape != b_.shape or not np.allclose(a, b_, rtol=0.0, atol=1e-12, equal_nan=True):', '            if False:'),
    ("X40 identity not enforced", '        if not ok:' + NL + '            hit("REFUSE.IDENTITY")', '        if False:' + NL + '            hit("REFUSE.IDENTITY")'),
    ("X41 outcome not write-once", '        if os.path.exists(U.P(p)):', '        if False:'),
    ("X42 median tau: upper middle", '    return float(xs[k // 2]) if k % 2 else 0.5 * (xs[k // 2 - 1] + xs[k // 2])', '    return float(xs[k // 2])'),
    ("X43 P2 Brier on the observed outcome only", '    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))',
     '    return float(sum((1.0 - p) ** 2 for o, p in probs if o == observed))'),
    ("X44 P6 read on BC0's tau*", '    mt = median_tau(st["tstar"]["AF"])', '    mt = median_tau(st["tstar"]["BC0"])'),
    ("X45 HB3 sign word on the 90% bounds", 'def sign_word(d):' + NL + '    """HB3: HB1\'s sign words only (no PARITY on EVAL)."""' + NL + '    if d["lo"] > 0:',
     'def sign_word(d):' + NL + '    """HB3: HB1\'s sign words only (no PARITY on EVAL)."""' + NL + '    if d["lo90"] > 0:'),
    ("X46 F-HB fired line dropped", '        hit("FHB.FIRED")' + NL + '        L.append(FHB_FIRES)', '        hit("FHB.FIRED")' + NL + '        L.append("")'),
    ("X47 F-BR fired line dropped", '        hit("FBR.FIRED")' + NL + '        L.append(FBR_FIRES % w["R1"])', '        hit("FBR.FIRED")' + NL + '        L.append("")'),
    ("X48 rule 8 TREE-BETTER at lo < 0", '    L.append("RULE 8: TREE-BETTER is %s (95%% lower bound %+.5f %s 0)" % ("REFUTED" if df["lo"] <= 0 else',
     '    L.append("RULE 8: TREE-BETTER is %s (95%% lower bound %+.5f %s 0)" % ("REFUTED" if df["lo"] < 0 else'),
    ("X49 TRAIN-CV with the bundle's K cells for BC (wrong arm)", '        arms["BC%d" % s] = TB.Arm("BC%d" % s, P_["H_bc"][s], [fl(vec[i]) for i in items], [fl(vec[i]) for i in gitems], m)',
     '        arms["BC%d" % s] = TB.Arm("BC%d" % s, P_["H_bc"][s], [fl(vec[i]) for i in items], [fl(vec[gitems[0]]) for i in gitems], m)'),
    ("X51 BC source root by the view's naming (alias MMLU_PRO_LB -> MMLU_PRO)", '        so = nm.split(":", 1)[0]', '        so = UCI.cell_member(nm)'),
    ("X50 BC seed s -> s + 1", '        h, C, cn, info = bc_build(H_af, Xt, tsrc, u["sources"], S["single"], s, under)',
     '        h, C, cn, info = bc_build(H_af, Xt, tsrc, u["sources"], S["single"], s + 1, under)'),
)

if __name__ == "__main__":
    sys.exit(main())
