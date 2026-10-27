"""union_cells_io.py: the shared, read-only loaders of CELL-FLIPS (cell_flips.py) and COVERAGE-AUDIT (coverage_audit.py), two
zero-call CPU readouts on the UNION-AF-ROUTE objects. ZERO calls; no write to any DB; no Gradle; no construction.

It imports union_af_route.py at blob:bf3f17db (refused otherwise; that module checks its own pins: g13_breakdown, g13_comparator,
rp12_pairing, v2_declared_cells blob:f0f56805) and reuses, unchanged:
  union_af_route.load_inputs    the inputs manifest (sha256-lf 53021e26..., pinned here) and every AF-U / inputs file re-hashed;
  v2_declared_cells.load_tree_cells / open_tw / pool_row / registry / side_items / cell_counts / structurally_complete /
  read_key / complete_items     G14's EVAL set (eval_view_REG.db, sha256-bytes pinned by v2_declared_cells), the key under
                                variant_rule UNUSABLE_CELL with the MATH-FIX overlay, exactly as leg U / UNION-AF-ROUTE read it;
  g13_breakdown.pool_check_v2   the B0-2 pool check (pv2 pools; replaces pool_guard.py, programme L22165).
The frozen TRAIN policy of UNION-AF-ROUTE (experiment_results/archv2/union_af_route/scratch/union_af_route_train_policy.json,
sha256-bytes 8d68018c..., the AF-U tree_cell, the K0 xtree_cell and the declared true_source_domain picks and best_single) is read,
never refitted.

Every path is resolved under the DATA ROOT (default: this checkout's root; --data-root in the two scripts), so the scripts can
run from a worktree against the main checkout's untracked outputs; nothing is ever written under the data root except the
write-once outcome files the scripts name.
"""
import os
import sys
import json
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


def sha256_crlf16(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


UA_PIN = "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"
if blob_lf(os.path.join(HERE, "union_af_route.py")) != UA_PIN:
    raise SystemExit("[UNION-CELLS] REFUSED: union_af_route.py is blob:%s, not the pinned blob:%s"
                     % (blob_lf(os.path.join(HERE, "union_af_route.py")), UA_PIN))
import union_af_route as UA      # noqa: E402  (checks its own pins; restores sqlite3.connect)
V = UA.V
RP = UA.RP
GB = UA.GB
G = V.G

# ── the objects of record (one dict; the selftests swap in their fixture's; nothing else writes _C) ─────────────────────────
CONST = dict(
    pool="pv2_1575de61bb20e977", cv="mc6-2026-09-11",
    n_eval=5907, comp_eval=5404,                      # G14's deciding set (Support (a) of both registrations)
    pool_items=6153, pool_comp=5642,                  # the pool row of the eval view
    roster=18, excluded=V.EXCLUDED,
    eval_rel=V.EVAL_REL.replace(os.sep, "/"), eval_sha=V.EVAL_SHA,
    gen_rel=V.GEN_REL.replace(os.sep, "/"), gen_sha=V.GEN_SHA,   # COVERAGE-AUDIT: GATE ids only (the OOS thresholds)
    policy_rel="experiment_results/archv2/union_af_route/scratch/union_af_route_train_policy.json",
    policy_sha="8d68018c013b7a770568b85d408a6fb027bb322f3219dded94e6b3a7d80a82fb",
    manifest_sha="53021e26e0eaa197c32895695ae61ab8c6535ec72a4d7a6799baf3119a5412a9",
    af_rel=UA.RES + "/inputs/af_cells.tsv", k0_rel=UA.RES + "/inputs/k_cells_s0.tsv",
    bundle_rel=UA.RES + "/inputs/af_u_bundle_256.npz", merged_rel=UA.RES + "/inputs/validation_merged",
    side_rel=RP.EP.DEFAULT_SIDE.replace(os.sep, "/"),
    texts_db="multicorpus_cache_v1.db", emb_db="embeddings_cache.db",
    rule="UNUSABLE_CELL",
    member_alias={"MMLU_PRO_LB": "MMLU_PRO"},          # cell / bundle naming -> the view's stratum_source naming
)
_C = [CONST]
_POOL = [GB.pool_check_v2]


def C():
    return _C[0]


def P(root, rel):
    return os.path.join(root, *rel.split("/"))


def member(name):
    """A member (view naming) from a cell prefix / class source / stratum_source."""
    s = str(name).split("/", 1)[0].split(":", 1)[0]
    return C()["member_alias"].get(s, s)


def cell_member(cell):
    """The construction member of a cell name: 'MMLU_PRO_LB:n00000152' / 'K0:BBH:003' / 'MMLU_PRO/biology'."""
    c = str(cell)
    if c.startswith("K") and c.count(":") == 2:
        return member(c.split(":")[1])
    return member(c)


def pool_line(say, tag):
    """THE FIRST PRINTED LINE of every mode: the B0-2 pool check (refusal on rc != 0 is a failed precondition)."""
    rc, msg = _POOL[0](C()["pool"])
    say("%s POOL %s: B0-2 pool check rc %d | %s" % (tag, C()["pool"], rc, msg))
    if rc != 0:
        raise SystemExit("%s REFUSED: the B0-2 pool check failed: %s" % (tag, msg))


def script_pins(say, tag, scripts):
    """Each script's identity: blob of the LF rendering (of record) and the working-tree bytes sha beside it."""
    for p in scripts:
        say("%s PIN %s blob:%s (LF rendering, of record); sha256-crlf16/working-tree bytes %s" % (
            tag, os.path.relpath(p, ROOT).replace(os.sep, "/"), blob_lf(p), sha256_crlf16(p)))


def write_once_check(paths, tag):
    ex = [p for p in paths if os.path.exists(p)]
    if ex:
        raise SystemExit("%s REFUSED: write-once output(s) exist: %s (outcome files of record are write-once; nothing read)" % (tag, ex))


def load_policy(root, say, tag):
    p = P(root, C()["policy_rel"])
    if not os.path.isfile(p):
        raise SystemExit("%s REFUSED: the frozen TRAIN policy %s is absent" % (tag, p))
    sh = sha256_bytes(p)
    say("%s FROZEN TRAIN POLICY %s sha256-bytes %s (%s)" % (tag, C()["policy_rel"], sh,
                                                            "= the pin" if sh == C()["policy_sha"] else "NOT the pin %s" % C()["policy_sha"]))
    if sh != C()["policy_sha"]:
        raise SystemExit("%s REFUSED: the frozen TRAIN policy is sha256 %s, not the pinned %s" % (tag, sh, C()["policy_sha"]))
    pol = json.load(open(p, encoding="utf-8"))
    for k in ("best_single", "roster", "tree_cell", "xtree_cell", "true_source_domain"):
        if k not in pol:
            raise SystemExit("%s REFUSED: the frozen policy lacks %s" % (tag, k))
    if "K0" not in pol["xtree_cell"]:
        raise SystemExit("%s REFUSED: the frozen policy carries no K0 arm" % tag)
    return pol


def load_cells(root, say, tag):
    """The inputs manifest through union_af_route.load_inputs (every AF-U and input file re-hashed), its sha pinned; the AF-U
    cells (R1, flatLeaf over all 123 cells) and the K_0 cells (seed 0, filed by source) through v2_declared_cells.load_tree_cells
    against the manifest's pins."""
    UA._ROOT[0] = root
    man, msh = UA.load_inputs(say)
    say("%s inputs manifest sha256 (LF) %s (%s)" % (tag, msh, "= the pin" if msh == C()["manifest_sha"] else "NOT the pin"))
    if msh != C()["manifest_sha"]:
        raise SystemExit("%s REFUSED: the inputs manifest is sha256 %s, not the pinned %s" % (tag, msh, C()["manifest_sha"]))
    af, d1 = V.load_tree_cells(P(root, C()["af_rel"]), man["inputs"][C()["af_rel"]])
    k0, d2 = V.load_tree_cells(P(root, C()["k0_rel"]), man["inputs"][C()["k0_rel"]])
    say("%s AF-U cells: %s" % (tag, d1))
    say("%s K_0 cells:  %s" % (tag, d2))
    return man, af, k0


def eval_set(root, say, tag, roster=None, key=False, marker=None):
    """G14's EVAL set. key=False: structure only (no key column; the tripwire stays sealed). key=True: the B1 marker (write-once)
    is written, then the ONE key read (UNUSABLE_CELL, MATH-FIX overlay). REFUSES unless the set is the registered n / components
    and (with the key) the key-complete set equals the structurally complete one."""
    c = C()
    path = P(root, c["eval_rel"])
    tw, esha = V.open_tw("eval", "route", path, c["eval_sha"], "eval_view", say)
    try:
        return _eval_set_open(tw, esha, path, root, say, tag, roster, key, marker)
    finally:
        tw.close()


def _eval_set_open(tw, esha, path, root, say, tag, roster, key, marker):
    c = C()
    nc, ni, _scope = V.pool_row(tw, c["pool"], c["cv"])
    if (nc, ni) != (c["pool_comp"], c["pool_items"]):
        raise SystemExit("%s REFUSED: the eval view's pool row is %d components / %d items, not %d / %d" % (
            tag, nc, ni, c["pool_comp"], c["pool_items"]))
    regm = V.registry(tw, c["cv"])
    models = sorted(m for m, s in regm.items() if s == "ACTIVE")
    if len(models) != c["roster"] or c["excluded"] in models or (roster is not None and list(roster) != models):
        raise SystemExit("%s REFUSED: the eval view's ACTIVE roster (%d) is not the frozen policy's %d-model roster without %s" % (
            tag, len(models), c["roster"], c["excluded"]))
    meta = V.side_items(tw, c["cv"], "EVAL")
    cc = V.cell_counts(tw, "response", c["cv"], models, meta)
    pre = V.structurally_complete(cc, models, c["rule"])
    K, kst = None, None
    if key:
        G.read_marker(marker, "%s: the EVAL key read started (B1); policy sha256 %s" % (tag, c["policy_sha"]))
        tw.unseal("%s: the one EVAL key read, after the frozen TRAIN policy sha256 %s was verified" % (tag, c["policy_sha"]))
        K, kst = V.read_key(tw, "response", c["cv"], models, meta, True, c["rule"])
        items = V.complete_items(K, models)
        if set(items) != pre:
            raise SystemExit("%s REFUSED: the key-complete EVAL set (%d) differs from the structurally complete one (%d)" % (
                tag, len(items), len(pre)))
    else:
        items = sorted(pre)
    ok = V.after_sha(path, esha, "eval_view", say)
    if not ok:
        raise SystemExit("%s REFUSED: the eval view's sha256 changed during the read" % tag)
    comps = len(set(meta[i][0] for i in items))
    say("%s EVAL SET (G14's: eval view EVAL items of %s, every one of the %d models with exactly one response, %s): %d items /"
        " %d components (registered %d / %d)%s" % (tag, c["cv"], len(models), c["rule"], len(items), comps, c["n_eval"], c["comp_eval"],
                                                  "" if not key else "; key cells single %d, multi %d, overlay rows %d (changed %d)" % (
                                                      kst["single"], kst["multi"], kst["overlay_rows"], kst["overlay_changed"])))
    if (len(items), comps) != (c["n_eval"], c["comp_eval"]):
        raise SystemExit("%s REFUSED: the EVAL set is %d items / %d components, not the registered %d / %d" % (
            tag, len(items), comps, c["n_eval"], c["comp_eval"]))
    return dict(items=items, meta=meta, models=models, K=K, kst=kst)


def kish(sizes):
    """Kish mean cluster size: sum n_g^2 / sum n_g."""
    s = np.asarray(list(sizes), dtype=np.float64)
    return float((s ** 2).sum() / s.sum()) if s.sum() > 0 else float("nan")


def pct(bs, q):
    """The g13_comparator percentile rule on a sorted list: lower bs[int(a B)], upper bs[int((1 - a) B) - 1]."""
    B = len(bs)
    return bs[int(q * B)] if q < 0.5 else bs[int(q * B) - 1]


def rmtree_ro(path):
    """Remove a temp tree that holds read-only (sealed) fixture files."""
    import shutil
    import stat

    def onerr(fn, p, _e):
        os.chmod(p, stat.S_IWRITE)
        fn(p)
    shutil.rmtree(path, onerror=onerr)
