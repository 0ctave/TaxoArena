"""union_route_common.py: the shared, read-only machinery of three zero-call CPU readouts on the UNION-AF-ROUTE objects,
registered 2026-10-04 (docs/judge_v2_program.md, record L24259-L24263, _as_of b66b075d):
  ROUTE-SOURCE-NULL  tools/analysis/route_source_null.py   (L24265-L24276)
  KNN-ROUTE          tools/analysis/knn_route.py           (L24278-L24289)
  KEY-INFO-V2        tools/analysis/key_info_v2.py         (L24291-L24302)
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. Readers only; nothing here writes except the
write-once marker / outcome helpers the three scripts call.

REUSED UNCHANGED (blob-pinned below; each pins its own dependencies):
  escalation_rc.py   (blob:8f99db7d) its import chain (union_af_route bf3f17db -> v2_declared_cells f0f56805, g13_breakdown,
                     g13_comparator, rp12_pairing); its read_views is the template of read_views here (gen view TRAIN key, then
                     the eval view after the frozen policy; [G14-NOROW]; the B1 marker mode "x"; the views' sha after); its
                     selftest layout (_build_layout / _clone) is the selftest fixture of the three scripts.
  union_cells_io.py  (blob:92a04543) kish (Kish mean cluster size), cell_member, the B0-2 pool / manifest constants.
  union_af_route.py  afu_state (D-8 commit, one-cell evidence S1-S6), load_inputs (every pinned AF-U / input file re-hashed),
                     input_paths, _POOL (the B0-2 pool check), _TV (rp12_pairing's text / vector readers), _VDC_CFG.
  v2_declared_cells.py (G14's reader) build_ud, fit, train_full, policy_json, run_boot, contrast, draw_units, _var: every policy
                     is fitted by V.fit (argmax over the sorted roster, a cell with TRAIN mass < 1 backs off to the best single).

THE OBJECTS (identical in the three registrations' DATA OBJECTS): content-closed v2 union split (draw 5a3e756), pool
pv2_1575de61bb20e977 (B0-2 pool check; a POOL READER: rule 7, never inside a construction); EVAL 5,907 items / 5,404
components (G14's set, variant_rule UNUSABLE_CELL, MATH-FIX overlay); 18 models (Meta-Llama-3-70B-Instruct excluded); AF-U as
built (inputs manifest sha256-lf 53021e26...); the frozen TRAIN policy of UNION-AF-ROUTE (sha256 8d68018c..., never committed);
two-stage bootstrap B 2,000, default_rng(42) (run_boot: TRAIN units resampled and every policy re-fitted, EVAL components
resampled within stratum); K_s = k_cells_s0..s4.tsv (seeds 0-4).
IDENTITY PRECONDITION (all three): the declared arm prints C1 +2.67pp [+1.46pp, +3.89pp] and AF-U prints G_AF +1.52pp
[+0.14pp, +2.91pp] (two-stage), with the arm accuracies best single 0.6049, TRUE source 0.6150, AF-U 0.6201, K0 0.6271 of the
UNION-AF-ROUTE outcome (sha256 e50a8e0f...); else the run refuses before any new number.
"""
import os
import sys
import json
import math
import hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_bytes(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


PINS = (("escalation_rc.py", "8f99db7d5745b21e61b10d08417c416fdb26875a"),
        ("union_cells_io.py", "92a04543b9c75eae5f37a76ae86eb189a190a9bd"),
        ("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"))
for _name, _pin in PINS:
    _p = os.path.join(HERE, _name)
    if blob_lf(_p) != _pin:
        raise SystemExit("[UNION-ROUTE-COMMON] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_p, blob_lf(_p), _pin))
import escalation_rc as ERC      # noqa: E402  (pins union_af_route, intent_transfer_s1, oos_baselines)
import union_cells_io as UCI     # noqa: E402  (pins union_af_route)
UAR = ERC.UAR
V, GB, RP, GC = UAR.V, UAR.GB, UAR.RP, UAR.GC
G = V.G
import sqlite3                   # noqa: E402
sqlite3.connect = getattr(sqlite3.connect, "_raw", sqlite3.connect)

POOL = "pv2_1575de61bb20e977"
SEEDS = (0, 1, 2, 3, 4)
KNAMES = tuple("K%d" % s for s in SEEDS)
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")

# the registered constants every script shares (each script copies them into its own REG; the selftests swap that dict)
COMMON = dict(
    pool=POOL, n_route=5907, comp_route=5404, B=2000, seed=42,
    uar_policy_sha="8d68018c013b7a770568b85d408a6fb027bb322f3219dded94e6b3a7d80a82fb",
    uar_outcome_sha="e50a8e0fa267db967981fb03320902c238fff505f00b1088d49c3c3a6596cd08",
    manifest_sha="53021e26e0eaa197c32895695ae61ab8c6535ec72a4d7a6799baf3119a5412a9",
    identity=dict(best="0.6049", tsrc="0.6150", af="0.6201", k0="0.6271", c1=("+2.67pp", "+1.46pp", "+3.89pp"),
                  g_af=("+1.52pp", "+0.14pp", "+2.91pp")),
    rws_n=200, rws_seed0=20261004,
)


def P(rel):
    return UAR.P(rel)


def pp(x):
    return "%+.2fpp" % (100.0 * x)


def in_band(x, band):
    """Numeric prediction bands: HELD iff the point lies in the CLOSED interval."""
    return bool(band[0] <= x <= band[1])


def brier(probs, observed):
    """Multi-outcome Brier sum: sum over outcomes of (p - [outcome observed])^2."""
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def pctl(xs, q):
    """The percentile rule of the three readouts: numpy percentile, linear interpolation (stated reading)."""
    return float(np.percentile(np.asarray(xs, dtype=np.float64), q))


def mc_se_pct(xs, q, B=2000, seed=20261004):
    """Monte Carlo SE of a percentile of the draws: the SD of the percentile over B resamples of the draws (fixed rng)."""
    x = np.asarray(xs, dtype=np.float64)
    rng = np.random.default_rng(seed)
    v = [float(np.percentile(x[rng.integers(0, len(x), len(x))], q)) for _ in range(B)]
    return float(np.std(v, ddof=1))


def header(say, test_id, mode, reg_text, files):
    say("POOL %s (%s; %s; the first line of every mode)" % (POOL, test_id, mode))
    say("%s | registration %s" % (test_id, reg_text))
    say("  results root %s; data root %s; calls 0 (zero-call CPU reader; no judge, no LLM, no embedding call, no build)" % (
        UAR._ROOT[0], RP.C.DATA_ROOT))
    for f in files:
        say("  " + G.identity_line(f))
    say("  threads: %s" % ", ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))


def frozen_policy(say, c, refuse, hit):
    pth = P(UAR.reg()["policy"])
    if not os.path.isfile(pth):
        hit("REFUSE.POLICY_ABSENT")
        refuse("UNION-AF-ROUTE's frozen TRAIN policy %s is absent" % UAR.reg()["policy"])
    sh = sha256_bytes(pth)
    if sh != c["uar_policy_sha"]:
        hit("REFUSE.POLICY_SHA")
        refuse("the frozen TRAIN policy %s is sha256 %s, not the registered %s" % (UAR.reg()["policy"], sh, c["uar_policy_sha"]))
    pol = json.load(open(pth, encoding="utf-8"))
    for k in ("best_single", "tree_cell", "xtree_cell", "true_source", "true_source_domain"):
        if k not in pol:
            refuse("the frozen policy lacks %s" % k)
    say("  frozen TRAIN policy %s sha256 %s (= the registered pin; never committed); best single %s; %d AF cells; K arms %s" % (
        UAR.reg()["policy"], sh, pol["best_single"], len(pol["tree_cell"]), ",".join(sorted(pol["xtree_cell"]))))
    return pol


def prepare(say, c, refuse, hit):
    """Everything before the key: the B0-2 pool check, the AF-U state, the inputs manifest (every file re-hashed), the AF and
    K0..K4 cells, the frozen TRAIN policy."""
    rc, msg = UAR._POOL[0](c["pool"])
    say("POOL CHECK (B0-2): rc %d | %s" % (rc, msg))
    if rc != 0:
        hit("REFUSE.POOL")
        refuse("the B0-2 pool check failed: %s" % msg)
    _pairs, _val, ksrc, _commit, single = UAR.afu_state(say)
    man, msha = UAR.load_inputs(say)
    if msha != c["manifest_sha"]:
        hit("REFUSE.MANIFEST")
        refuse("the inputs manifest is sha256 (LF) %s, not the pinned %s" % (msha, c["manifest_sha"]))
    if man["ksrc"] != ksrc:
        refuse("the inputs were built at leaf counts %s, the AF-U snapshots now give %s" % (man["ksrc"], ksrc))
    ip = UAR.input_paths()
    af, d1 = V.load_tree_cells(P(ip["af"]), man["inputs"][ip["af"]])
    kx = {}
    for s in SEEDS:
        kx["K%d" % s], _d = V.load_tree_cells(P(ip["k"][s]), man["inputs"][ip["k"][s]])
    say("  AF-U cells: %s" % d1)
    say("  K_s cells: k_cells_s0..s4.tsv (seeds 0-4), every one equal to its manifest pin")
    pol = frozen_policy(say, c, refuse, hit)
    return dict(af=af, kx=kx, pol=pol, ksrc=ksrc, single=single, man=man, msha=msha)


def read_views(cfg, say, dry, af, kx, marker_path, marker_text, refuse, hit, between=None, tag=""):
    """escalation_rc.read_views with this test's marker and the K0..K4 arms: the gen view (TRAIN key) and, unless dry, the eval
    view (EVAL key). `between(K_tr, train_meta, models)` runs after the TRAIN key and BEFORE the eval view opens (no EVAL)."""
    rule = cfg.pre.get("variant_rule")
    say("--- TRAIN (gen_view, open_generation('policy_fit')) ---")
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view", say)
    nc, ni, scope = V.pool_row(tw, cfg.pool_u, cfg.cv_u)
    say("  pool %s (scope %r): %d components, %d items of %s" % (cfg.pool_u, scope, nc, ni, cfg.cv_u))
    if nc != cfg.reg["comp_eval_u"] or ni != cfg.reg["n_eval_u"]:
        refuse("pool counts %d / %d differ from the registration's %d / %d" % (nc, ni, cfg.reg["comp_eval_u"], cfg.reg["n_eval_u"]))
    regm = V.registry(tw, cfg.cv_u)
    models = sorted(m for m, s in regm.items() if s == "ACTIVE")
    say("  roster (ACTIVE, sorted = the argmax tie-break order): %d (registered %d); %s absent: %s" % (
        len(models), cfg.reg["roster_u"], V.EXCLUDED, V.EXCLUDED not in models))
    if len(models) != cfg.reg["roster_u"] or V.EXCLUDED in models:
        refuse("roster check failed")
    train_meta = V.side_items(tw, cfg.cv_u, "TRAIN")
    comp_strata = V.component_strata(tw)
    cc_tr = V.cell_counts(tw, "response_lite", cfg.cv_u, models, train_meta)
    say("  TRAIN items %d; structurally key-complete under %s: %d" % (len(train_meta), rule, len(V.structurally_complete(cc_tr, models, rule))))
    if dry:
        tw.close()
        V.after_sha(cfg.gen_path, gsha, "gen_view", say)
        say("  eval_view %s pinned sha256-bytes %s: NOT opened by --dry-run" % (cfg.eval_path, cfg.eval_sha))
        return None, None
    tw.unseal("%s: the TRAIN key for the per-replicate policy fits (the frozen policy is checked beside EVAL)" % tag)
    K_tr, kst_tr = V.read_key(tw, "response_lite", cfg.cv_u, models, train_meta, True, rule)
    tw.close()
    ok_g = V.after_sha(cfg.gen_path, gsha, "gen_view", say)
    say("  TRAIN key: cells single %d, multi %d (unusable %d); MATH-FIX overlay rows %d, value changed %d; key rows fetched %d" % (
        kst_tr["single"], kst_tr["multi"], kst_tr["multi_unusable"], kst_tr["overlay_rows"], kst_tr["overlay_changed"], kst_tr["key_rows_fetched"]))
    if between is not None:
        between(K_tr, train_meta, models)
    say("--- EVAL (eval_view, open_eval('route'); after the frozen TRAIN policy file) ---")
    V.b3_guard(cfg)
    tw, esha = V.open_tw("eval", "route", cfg.eval_path, cfg.eval_sha, "eval_view", say)
    nc2, ni2, _ = V.pool_row(tw, cfg.pool_u, cfg.cv_u)
    if (nc2, ni2) != (nc, ni):
        refuse("eval_view pool row differs from gen_view's")
    eval_meta = V.side_items(tw, cfg.cv_u, "EVAL")
    if sorted(m for m, s in V.registry(tw, cfg.cv_u).items() if s == "ACTIVE") != models:
        refuse("eval_view's roster differs from gen_view's")
    cc_ev = V.cell_counts(tw, "response", cfg.cv_u, models, eval_meta)
    pre_ok = V.structurally_complete(cc_ev, models, rule)
    say("  EVAL items %d (%d components); structurally key-complete under %s: %d" % (
        len(eval_meta), len(set(v[0] for v in eval_meta.values())), rule, len(pre_ok)))
    for nm, cells in [("AF-U", af)] + sorted(kx.items()):
        norow = sorted(i for i in pre_ok if cells.get(i, V.NO_ROUTING_ROW) == V.NO_ROUTING_ROW)
        say("  %s: EVAL items of the scoring set without a cell: %d (must be 0)" % (nm, len(norow)))
        if norow:
            hit("REFUSE.NOROW")
            refuse("[G14-NOROW] %s: %d EVAL item(s) of the scoring set have no cell (first %s); refused before the EVAL key read"
                   % (nm, len(norow), norow[:3]))
    G.read_marker(P(marker_path), marker_text)
    hit("MARKER.WRITTEN")
    tw.unseal("%s route read of EVAL (marker %s written)" % (tag, marker_path))
    K_ev, kst_ev = V.read_key(tw, "response", cfg.cv_u, models, eval_meta, True, rule)
    tw.close()
    ok_e = V.after_sha(cfg.eval_path, esha, "eval_view", say)
    say("  EVAL key: cells single %d, multi %d (unusable %d); MATH-FIX overlay rows %d, value changed %d; key rows fetched %d" % (
        kst_ev["single"], kst_ev["multi"], kst_ev["multi_unusable"], kst_ev["overlay_rows"], kst_ev["overlay_changed"], kst_ev["key_rows_fetched"]))
    D = V.build_ud(models, train_meta, eval_meta, K_tr, K_ev, comp_strata, cfg.pre["train_unit"], None, cfg.reg["placebo_seed"],
                   tree=af, xtrees=dict(kx))
    D.fit_asserts = 0
    return D, (ok_g and ok_e)


def check_denominators(D, c, refuse, hit, tag):
    n_comp = D.eval_units["n_units"]
    if (D.n_eval, n_comp) != (c["n_route"], c["comp_route"]):
        hit("REFUSE.DENOM")
        refuse("[%s-DENOM] the scored set is %d items / %d components, not the registered %d / %d" % (
            tag, D.n_eval, n_comp, c["n_route"], c["comp_route"]))
    return n_comp


def b3_check(D, cfg, pol, refuse, hit):
    """The point policy re-fitted beside EVAL must equal UNION-AF-ROUTE's frozen file in every arm it carries."""
    P0 = V.fit(D, V.train_full(D))
    pj = V.policy_json(D, P0, cfg, "")

    def nn(d):
        return {k: v for k, v in d.items() if v is not None}
    bad = []
    if D.models[P0.gb] != pol["best_single"]:
        bad.append("best_single")
    for k in ("tree_cell", "true_source", "true_source_domain"):
        if nn(pj[k]) != nn(pol[k]):
            bad.append(k)
    for nm in KNAMES:
        if nm not in pol["xtree_cell"] or nn(pj["xtree_cell"][nm]) != nn(pol["xtree_cell"][nm]):
            bad.append("xtree_cell." + nm)
    if bad:
        hit("REFUSE.B3")
        refuse("[B3] the point policy re-fitted beside EVAL differs from UNION-AF-ROUTE's frozen file in %s" % bad)
    return P0


def karm(D, nm):
    return 6 + sorted(D.xnames).index(nm)


def identity(bt, D, idn):
    """-> (ok, got): the arm digits (4 dp) and the C1 / G_AF strings, read exactly as UNION-AF-ROUTE printed them."""
    got = dict(best="%.4f" % bt["point"][0, V.BS], tsrc="%.4f" % bt["point"][0, V.TSRC], af="%.4f" % bt["point"][0, V.TREE],
               k0="%.4f" % bt["point"][0, karm(D, "K0")])
    c1 = V.contrast(bt, D, "ALL", V.TDOM, V.BS)
    ga = V.contrast(bt, D, "ALL", V.TREE, V.BS)
    got["c1"] = (pp(c1["point"]), pp(c1["lo"]), pp(c1["hi"]))
    got["g_af"] = (pp(ga["point"]), pp(ga["lo"]), pp(ga["hi"]))
    ok = all(got[k] == idn[k] for k in ("best", "tsrc", "af", "k0")) and tuple(got["c1"]) == tuple(idn["c1"]) \
        and tuple(got["g_af"]) == tuple(idn["g_af"])
    return ok, got


def identity_text(got):
    return ("best single %s, TRUE source %s, AF-U leaf cell %s, K_s K0 %s; C1 %s [%s, %s]; G_AF %s [%s, %s]"
            % ((got["best"], got["tsrc"], got["af"], got["k0"]) + tuple(got["c1"]) + tuple(got["g_af"])))


class _Lite:
    pass


def point_fit(D, g, ng):
    """G14's reader (V.fit, unchanged) on ONE extra grouping over every scored position, fitted on the full TRAIN.
    -> (per-cell model index, -1 = no TRAIN mass; best single index)."""
    L = _Lite()
    m = len(D.models)
    L.A, L.models, L.train_set, L.fit_asserts = D.A, D.models, D.train_set, 0
    L.groupings = {"x": (np.asarray(g, dtype=np.int64), int(ng))}
    L.flat = {"x": (L.groupings["x"][0][:, None] * m + np.arange(m)[None, :]).ravel()}
    Pp = V.fit(L, V.train_full(D))
    return Pp.pol["x"], Pp.gb


def routed_correct(D, pol, gb, g):
    """Per-EVAL-position correctness of the per-cell policy (a cell without TRAIN mass -> the best single)."""
    pe = pol[np.asarray(g)[D.E]]
    mod = np.where(pe < 0, gb, pe)
    return D.A[D.E, mod].astype(np.float64)


def rws_profile(D, g_af):
    """AF-U's per-source size profile on the scored TRAIN items: {source: [TRAIN size of each AF cell met in that source, in AF
    cell-index order]} (the source = the item's stratum source, D.src)."""
    prof = {}
    for s in sorted(set(D.src)):
        pos = [k for k in D.T if D.src[k] == s]
        cnt = {}
        for k in pos:
            cnt[int(g_af[k])] = cnt.get(int(g_af[k]), 0) + 1
        prof[s] = [cnt[j] for j in sorted(cnt)]
    return prof


def rws_cells(D, prof, seed):
    """One RWS draw: within each source (sorted), a uniformly random permutation of its scored TRAIN items (position order) cut into
    blocks of AF-U's sizes (profile order); then each EVAL item of the source is filed to a random cell of its source drawn with
    the TRAIN size weights. One default_rng(seed) stream, in this order. -> (grouping over all positions, number of cells)."""
    rng = np.random.default_rng(seed)
    g = np.full(D.n, -1, dtype=np.int64)
    base = 0
    srcs = sorted(prof)
    starts = {}
    for s in srcs:
        pos = np.array([k for k in D.T if D.src[k] == s], dtype=np.int64)
        sizes = prof[s]
        if sum(sizes) != len(pos):
            raise SystemExit("[RWS] source %s: profile sizes sum %d != %d TRAIN items" % (s, sum(sizes), len(pos)))
        perm = rng.permutation(len(pos))
        off = 0
        for j, sz in enumerate(sizes):
            g[pos[perm[off:off + sz]]] = base + j
            off += sz
        starts[s] = base
        base += len(sizes)
    for s in srcs:
        epos = np.array([k for k in D.E if D.src[k] == s], dtype=np.int64)
        if not len(epos):
            continue
        w = np.asarray(prof[s], dtype=np.float64)
        g[epos] = starts[s] + rng.choice(len(w), size=len(epos), p=w / w.sum())
    if (g < 0).any():
        raise SystemExit("[RWS] %d scored item(s) of a source without TRAIN items" % int((g < 0).sum()))
    return g, base


def interval(pt, two, iid, n, z=1.96):
    """G14's reader form: point +- z SE_2stage; i.i.d. SE beside -> DEFF, n_eff, MDE80 = 2.80 SE_2stage."""
    v2, vi = V._var(two), V._var(iid)
    se2, sei = math.sqrt(v2), math.sqrt(vi)
    deff = v2 / vi if vi > 0 else float("nan")
    return dict(point=float(pt), se2=se2, se_iid=sei, lo=pt - z * se2, hi=pt + z * se2, lo90=pt - 1.645 * se2, hi90=pt + 1.645 * se2,
                pct=tuple(float(x) for x in np.nanpercentile(np.asarray(two, dtype=np.float64), [2.5, 97.5])) if len(two) else (pt, pt),
                deff=deff, n_eff=(n / deff) if deff == deff and deff > 0 else float("nan"), mde=2.80 * se2, n=n)


def iid_weights(seed, NE, B):
    """run_boot's i.i.d. draws (default_rng(seed), EVAL items i.i.d., policy fixed), regenerated in the same order."""
    rng = np.random.default_rng(seed)
    for _b in range(B):
        yield np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)


def kish_eval(D):
    from collections import Counter
    return UCI.kish(Counter(D.comp[k] for k in D.E).values())


def write_outcome(path_rel, text, ok_sha, refuse, out):
    if not ok_sha:
        G.write_once(P(path_rel).replace(".txt", "_VOID.txt"), text + "[VOID] a view's sha differs after the read\n")
        refuse("[PIN] a view's sha256 differs after the read: outcome written to _VOID, not to the file of record")
    G.write_once(P(path_rel), text)
    out("OUTCOME written write-once: %s (sha256 %s; never committed: back up to E:/TaxoArena_backup_<date>_<tag> with SHA256SUMS.txt)"
        % (path_rel, hashlib.sha256(text.encode("utf-8")).hexdigest()))


def pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


# ══ SELFTEST HELPERS (fixtures and independent oracles; mutants of this module edit only the code ABOVE this line) ══════

import io            # noqa: E402
import re            # noqa: E402
import contextlib    # noqa: E402
from collections import defaultdict   # noqa: E402


def build_layout(tmp):
    """escalation_rc's selftest layout (union_af_route's fixture with a one-cell member, --build-inputs and --run executed on
    v2_declared_cells' sealed fixture views) plus the identity strings this module checks, read off the fixture's own
    UNION-AF-ROUTE outcome."""
    lay0 = ERC._build_layout(tmp)
    t = lay0.uar_out
    m = re.search(r"IDENTITY PRECONDITION: the declared arm C1 = ([+-][0-9.]+pp) \[([+-][0-9.]+pp), ([+-][0-9.]+pp)\]", t)
    ts = re.search(r"^    TRUE source\s+([0-9.]+)\s", t, re.M).group(1)
    idn = dict(lay0.reg["identity"], tsrc=ts, c1=(m.group(1), m.group(2), m.group(3)))
    man = os.path.join(tmp, "res", "inputs", "inputs_manifest.json")
    lay0.common = dict(COMMON, n_route=lay0.reg["n_route"], comp_route=lay0.reg["comp_route"], B=lay0.reg["B"], seed=lay0.reg["seed"],
                       uar_policy_sha=lay0.reg["uar_policy_sha"], uar_outcome_sha=lay0.reg["uar_outcome_sha"],
                       manifest_sha=UAR.sha256_lf(man), identity=idn, rws_n=40)
    return lay0


def clone(lay, dest):
    new = ERC._clone(lay, dest)
    new.common = dict(lay.common)
    return new


@contextlib.contextmanager
def mine(mod, lay, **over):
    saved = mod._REG[0]
    mod._REG[0] = dict(mod.REG, **dict(lay.common, **dict(mod.FIXTURE_REG, **over)))
    try:
        with UAR._patched(lay.fx):
            yield
    finally:
        mod._REG[0] = saved


def cap(mod, fn, lay, **over):
    buf = io.StringIO()
    with mine(mod, lay, **over):
        with contextlib.redirect_stdout(buf):
            try:
                res = fn(out=lambda s: print(s, flush=True))
                err = None
            except SystemExit as e:
                res, err = None, str(e)
    return buf.getvalue(), err, res


def need(text, *needles):
    for n in needles:
        if n not in text:
            raise AssertionError("missing %r" % n[:240])


def num(text, pat):
    mm = re.search(pat, text)
    if not mm:
        raise AssertionError("no line %r" % pat)
    return [float(x) for x in mm.groups()]


def o_key(spec):
    """The fixture's keyed correctness from its raw response rows (escalation_rc's oracle reader)."""
    return ERC._o_key(spec)


def o_fit(tr, cells, val, mu, w=None):
    """Plain-loop policy fit: best single = the model with the largest weighted TRAIN total (ties -> first in sorted roster); per
    cell the same within the cell; a cell without TRAIN mass is absent (-> best single)."""
    w = w if w is not None else {i: 1 for i in tr}
    tot = {m_: sum(w.get(i, 0) * val[(i, m_)] for i in tr) for m_ in mu}
    best = max(mu, key=lambda m_: (tot[m_], -mu.index(m_)))
    per = defaultdict(lambda: defaultdict(float))
    mass = defaultdict(float)
    for i in tr:
        if w.get(i, 0):
            mass[cells[i]] += w[i]
            for m_ in mu:
                per[cells[i]][m_] += w[i] * val[(i, m_)]
    pol = {c_: max(mu, key=lambda m_: (per[c_][m_], -mu.index(m_))) for c_ in per if mass[c_] >= 1}
    return best, pol


def o_acc(ev, cells, val, best, pol, v=None):
    v = v if v is not None else {i: 1 for i in ev}
    tot = sum(v[i] for i in ev)
    return sum(v[i] * val[(i, pol.get(cells[i], best))] for i in ev) / tot


def o_rws(tr, ev, src, af, seed):
    """Plain-loop RWS draw on the registered rng protocol (route_source_null R3): -> {item: (source, block)}."""
    from collections import Counter
    sources = sorted(set(src[i] for i in tr))
    trs = {s: [i for i in tr if src[i] == s] for s in sources}
    rr = np.random.default_rng(seed)
    prof = {}
    for s in sources:
        cnt = Counter(af[i] for i in trs[s])
        prof[s] = [cnt[cl] for cl in sorted(cnt)]
    cell = {}
    for s in sources:
        perm = rr.permutation(len(trs[s]))
        off = 0
        for j, sz in enumerate(prof[s]):
            for q in perm[off:off + sz]:
                cell[trs[s][q]] = (s, j)
            off += sz
    for s in sources:
        es = [i for i in ev if src[i] == s]
        if not es:
            continue
        wts = np.array(prof[s], float)
        dr = rr.choice(len(wts), size=len(es), p=wts / wts.sum())
        for i, j in zip(es, dr):
            cell[i] = (s, int(j))
    return cell


def run_selftest(tag, cases, fns, hitc, only=None, quiet=False, base=None):
    import tempfile
    import scratch_dir   # noqa: F401  TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="urc_")
        made.append(d)
        return os.path.join(d, "lay")
    hitc.clear()
    try:
        for name, desc, kind in cases:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                if kind == "base" and base is None:
                    with contextlib.redirect_stdout(io.StringIO()):
                        base = build_layout(mk())
                with contextlib.redirect_stdout(io.StringIO()):
                    fn = fns[name]
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
        print("%s selftest: %d / %d passed" % (tag, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(script_path, script_modname, mutants, tag, only=None):
    """Each mutant edits the code ABOVE the SELFTEST marker of the script ('S' target) or of this module ('C' target) in memory,
    executes the edited module(s) and runs the script's selftest on one fixture layout built by the unedited code; KILLED iff
    the selftest fails. The control X00 must survive."""
    import types
    import tempfile
    import scratch_dir   # noqa: F401
    import shutil
    NL = chr(10)
    mark = NL + "# " + chr(0x2550) * 2 + " SELFTEST"
    ssrc = open(script_path, encoding="utf-8").read()
    csrc = open(os.path.abspath(__file__), encoding="utf-8").read()
    s_cut, c_cut = ssrc.index(mark), csrc.index(mark)
    d = tempfile.mkdtemp(prefix="urc_mut_")
    rows, bad = [], []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            base = build_layout(os.path.join(d, "lay"))
        for name, target, old, new in mutants:
            if only and not any(name.startswith(o) for o in only):
                continue
            head = ssrc[:s_cut] if target == "S" else csrc[:c_cut]
            if old and head.count(old) != 1:
                bad.append(name)
                rows.append((name, "NOT APPLIED (%d matches)" % head.count(old)))
                print("  %-72s NOT APPLIED (%d matches)" % (name, head.count(old)), flush=True)
                continue
            try:
                cmod = sys.modules[__name__]
                if target == "C" and old:
                    cmod = types.ModuleType("union_route_common_mutant")
                    cmod.__file__ = os.path.abspath(__file__)
                    exec(compile(csrc[:c_cut].replace(old, new) + csrc[c_cut:], cmod.__file__, "exec"), cmod.__dict__)
                mod = types.ModuleType(script_modname + "_mutant")
                mod.__file__ = script_path
                code = (ssrc[:s_cut].replace(old, new) if (target == "S" and old) else ssrc[:s_cut]) + ssrc[s_cut:]
                exec(compile(code, mod.__file__, "exec"), mod.__dict__)
                mod.U = cmod
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.selftest(quiet=True, base=base)
                res = "SURVIVED"
            except BaseException as e:   # noqa: B902
                res = "KILLED (%s)" % type(e).__name__
            rows.append((name, res))
            print("  %-72s %s" % (name, res), flush=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        tag, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0
