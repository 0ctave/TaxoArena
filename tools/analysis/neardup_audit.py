"""NEARDUP-AUDIT (zero calls; CPU readout; tree_uses E3): is the anchored tree bareq512_s42 a safe BLOCKING index for a
near-duplicate audit? The CK-CLOSE-v1 stem_key twins between p2dca EVAL and bareq512_s42's TRAIN members are the
positives; 'same leaf + cos >= 0.95' (TREE-BLOCK, deciding) against a plain cosine threshold over all of TRAIN (PLAIN),
with a spherical k-means blocking arm beside (KMEANS-BLOCK, descriptive).

REGISTRATION: docs/judge_v2_program.md L24169-L24181 (_as_of fac3d50b), heading
  "## Registered 2026-10-04 (before any code or call) — NEARDUP-AUDIT: with the known CK-CLOSE-v1 stem_key twins between
   p2dca EVAL and bareq512_s42's TRAIN members as positives, does 'same leaf + high cosine' recover them as well as a plain
   cosine threshold over all of TRAIN, at a fraction of the comparisons, with a k-means blocking arm beside? (zero calls;
   CPU readout; tree_uses E3)"
Results JSON: docs/agents/results/NEARDUP-AUDIT.json. The criterion, predictions and falsifier are quoted in CRITERIA below
and printed verbatim by --run; their numbers are not changed here.

LAUNCH SEQUENCE (plain form; from the main checkout, or with TAXOARENA_DATA_ROOT naming the directory holding the DBs):
    python tools/analysis/neardup_audit.py --selftest     # synthetic, opens no DB of record; mutant table below
    python tools/analysis/neardup_audit.py --dry-run      # copies, guards, loads; prints pins, denominators, the positive
                                                          # count and the planned support; reads NO cosine, writes nothing
    python tools/analysis/neardup_audit.py --run          # the readout of record: write-once outcome + SHA256SUMS on E:
There is no --pilot, no cache and no --analyze: the test posts no call (no judge, no truncation guard has an object); --run
computes and writes the outcome in one step from inputs that are complete by construction.

HYGIENE (registration HYGIENE; brief 2026-10-04):
  * the three DBs read (mmlu_pro_dataset_cache_v2.db, embeddings_cache.db, snapshots.db) are COPIED (db, plus -wal when
    non-empty; a non-empty -journal refuses: a writer is active) into tempfile.mkdtemp(dir=E:/TaxoArena_tmp), the source
    stat is compared before and after the copy (a change refuses), and only the copies are opened, through
    pool_guard.open_ro (mode=ro&immutable=1 after the -wal check). The scratch dir is removed in a finally block.
    snapshots_frozen.db is never opened. Zero calls.
  * pool_guard.assert_pool_of_record(p2dca21ab5f4ef3ae) is the first printed line (run on the copies).
  * outputs are never committed: --run writes OUT_DIR/neardup_audit_outcome.txt (mode 'x', write-once) and
    OUT_DIR/SHA256SUMS.txt (mode 'x'); OUT_DIR defaults to E:/TaxoArena_backup_2026-10-04_neardup_audit.

OBJECTS (registration OBJECTS AND POSITIVES; refused if the counts differ):
  tree bareq512_s42 = snapshots.db snapshot 20260909_212117_Headless_Run_Auto_ge, 87 leaves (nodes without childIds),
  8,278 distinct TRAIN members (leaf queryIds, 'q_' + sha256(raw_text)[:16], mapped by embeddings_cache.queries.id to the
  text; the queries.query_id column is never used), qwen3 4096-d vectors sliced to the first 512 dims and unit-normed
  (anchor_free_readout.sliced's rule, R512). EVAL = pool_guard.eval_ids(p2dca21ab5f4ef3ae) (3,445 judgeable ids), text =
  the linked mmlu_pro row (content_closure._load_p2dca's join, eval_question_link.mmlu_pro_row_id; no text join).
  POSITIVES = (EVAL id, TRAIN member) pairs with content_closure.ck_key(eval stem) == ck_key(member text) (CK-CLOSE-v1,
  content_closure.py blob 1533cb5a, verified at start), counted and printed before any cosine is read (--dry-run stops
  there). Tiers (descriptive, disjoint): EXACT (identical stem text), SAME-OPTIONS (not exact; some mmlu_pro row carrying
  the member text has split_side.content_key(stem, options, "") equal to the EVAL row's), STEM-ONLY (the rest).

READINGS where the registration is silent (fixed before any data were read; each is printed by --run):
  R1 leaf membership = the leaf's queryIds list: a member listed in several leaves (soft membership) is in each of those
     blocks; "the TRAIN members of the leaf it files into" is that list. The primary-leaf-only block (max queryWeight)
     is a printed SENSITIVITY line, not the criterion.
  R2 flatLeaf centroid of a leaf = unit(mean of the unit R512 vectors of the members it lists) (unweighted; "TRAIN-member
     means (unit, R512)"); cos to the stored vmfMu and the filing agreement with vmfMu filing are printed descriptively.
  R3 ND1 bootstrap: B = 2,000, seed 20261004, percentile 95% interval, resampling EVAL ids that carry at least one
     deciding pair (pairs clustered by EVAL id), statistic = ratio of sums. ND1 is not computable (REFUSED, nothing written)
     when no positive pair is PLAIN-flagged at tau 0.95: the criterion would have no object.
  R4 comparison fraction: P3 is scored on the REGISTERED statistic "mean leaf size / 8,278" (unweighted mean of the
     87 leaves' listed sizes; READY_neardup_audit C-3); the EVAL-weighted mean block size / 8,278 is printed beside it as
     the "R4 reading" (descriptive).
  C-2 (READY_neardup_audit; FLAGGED FOR THE REGISTRAR, a rule the registration does not carry): the exact two-sided 95%
     Clopper-Pearson upper bound on misses / deciding pairs is printed beside the bootstrap upper bound. When the
     bootstrap interval is degenerate (zero width, e.g. 0 misses -> [0, 0]) the CP upper bound decides ND1; otherwise
     the registered bootstrap decides and both verdicts are printed, any difference named.
  C-1: the primary-leaf-only sensitivity prints its point, the same cluster-bootstrap interval and its verdict, and
     "R1-DEPENDENT" when that verdict differs from ND1's.
  R5 KMEANS-BLOCK: flat_mix_mmlu.spherical_kmeans / kmeanspp (k-means++ on the sphere, 300 iterations), extracted from
     flat_mix_mmlu.py by AST at its pinned blob (importing that module would patch sqlite3.connect), k = 87 on the 8,278
     member vectors, seeds 0-4; members carry their fit labels, EVAL items the nearest centroid; BLOCK-LOSS per seed and
     the seed mean (P4 scores the mean).
  R6 measured support: the Kish mean cluster size m = sum n_i^2 / sum n_i of the DECIDING pairs by EVAL id (DEFF at
     rho = 1, an upper bound) is the measured DEFF used for n_eff, the realised SE and MDE80 = 2.8 x SE; the bootstrap
     variance ratio var_boot / (p(1-p)/n) is printed beside when p is in (0, 1). The declared DEFF 1.2 is printed against
     it. Wrong(established) counts and the two tie conventions have no object here (no judge direction is scored).

CRITERIA (verbatim from the registration):
  ND1 (DECIDING; the INTERVAL decides): BLOCK-LOSS = share of the positives PLAIN flags at tau 0.95 that TREE-BLOCK misses
  (their twin sits in another leaf); 95% interval by bootstrap over EVAL ids (pairs clustered by EVAL id). BLOCKS-WELL iff
  the 95% upper bound <= 0.10; LOSES iff the point > 0.10; UNDETERMINED otherwise. FAILS (rule 8): BLOCKS-WELL is refuted
  by a point above 0.10.
  P1 BLOCK-LOSS 0.03 [0.00, 0.08]; ND1 BLOCKS-WELL 0.65, UNDETERMINED 0.20, LOSES 0.15. P2 PLAIN recall at tau 0.95 0.80
  [0.60, 0.95]. P3 comparison fraction 0.02 [0.01, 0.04]. P4 KMEANS-BLOCK BLOCK-LOSS 0.03 [0.00, 0.10] (descriptive).
  F-ND fires iff ND1 reads LOSES.

SELFTEST: synthetic fixtures through main() with an injected loader (the --run and --dry-run entry points of record), the
assembly step on a synthetic graph, and the write-once / pin refusals; every ND1 verdict, the F-ND branch both ways, each
of P1-P4 HELD and FAILED, both refusals, and the support lines are asserted by VALUE. Run it under python and python -O.

MUTANT TABLE (each a temporary edit, selftest re-run, edit reverted; 2026-10-04):
  M1  ND1 LOSES test `point > BAR` -> `point >= BAR`                                  killed (F4: 4/40 must read UNDETERMINED)
  M2  ND1 BLOCKS-WELL test `hi <= BAR` -> `hi < BAR`                                  killed (verdict table row 0.05/[0.00,0.10])
  M3  denominator = all positives instead of the PLAIN-flagged ones                   killed (F1 sub-threshold twins)
  M4  tree block = primary leaf only (R1 broken)                                      killed (multi-leaf member fixture)
  M5  flatLeaf filing on the stored vmfMu instead of member means (R2 broken)         killed (fixture vmfMu deliberately rotated)
  M6  filing argmax -> argmin (min<->max)                                             killed
  M7  deciding tau 0.95 -> 0.90                                                       killed (F1 twins at cos ~0.92 missed by the tree)
  M8  bootstrap over pairs instead of EVAL ids                                        killed (cluster count / Kish lines, F5)
  M9  P3 from the unweighted mean leaf size                                           killed (F6 unequal leaves)
  M10 outcome opened 'w' instead of 'x'                                               killed (second --run must refuse, file unchanged)
  M11 positives keyed on exact text instead of stem_key                               killed (F1 count; tiny fixtures refuse)
  M12 k-means seeds (0,) instead of 0-4                                               killed (printed seed list)
  M13 F-ND line omitted on the not-fired branch                                       killed
  M14 Kish m from all positives instead of the deciding pairs                         killed (F1 m = 1.100 exactly)
  M15 P2 interval upper 0.95 -> 1.00                                                  killed (F2 recall 1.000 must FAIL)
  M16 refusal on zero PLAIN-flagged positives removed                                 killed (the run crashes, nothing written)
  M17 zero positives refusal removed                                                  killed
  M18 dry-run reads cosines (analyze called)                                          killed (dry-run sentinel)
  M19 EVAL side = TRAIN members (wrong population) in assemble()                      killed (assemble fixture: EVAL ids / member ids)
  M20 tier EXACT on norm-equal text                                                   killed (tier counts)
  20/20 killed; no survivor on a deciding path (harness: each edit applied to this file, --selftest re-run, file restored).
DELTA after READY_neardup_audit (C-1..C-4; 2026-10-04): M9 now reads "P3 scored on the EVAL-weighted fraction" (C-3), killed;
  O1  upper percentile 97.5 -> 95 (a 90% interval decides)                            killed (F3 [0.000, 0.175] pinned, C-4)
  C2a CP never decides (degenerate bootstrap decides)                                 killed (F1 CP 0.077; F7 0/30 CP 0.116)
  C2b CP always decides                                                               killed (F3: bootstrap 0.175 decides, CP 0.204)
  C2c CP one-sided 95% instead of two-sided                                           killed (F1 0.077 = 1 - 0.025^(1/46))
  C1a primary-only interval computed on the R1 misses                                 killed (F1 [0.000, 0.068])
  C1b R1-DEPENDENT never printed                                                      killed (F8 6/51 = 0.118 LOSES)
  26/26 killed (the 20 above re-run with M9 inverted, plus 6). O4 (DIM never sliced in fixtures, C-5) left to the
  post-run PIN check as the review allows.
DRY-RUN OF RECORD INPUTS (2026-10-04, at the build): positives 70 pairs over 70 EVAL ids (EXACT 37, SAME-OPTIONS 33,
STEM-ONLY 0), below the planning 150 / 135: the --run prints the realised SE and MDE (registration SUPPORT (g)).
"""
import argparse
import ast
import datetime
import hashlib
import json
import os
import shutil
import sqlite3
import struct
import sys
import tempfile
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
sys.path.insert(0, HERE)

TAG = "[NEARDUP]"
TEST_ID = "NEARDUP-AUDIT"
POOL_ID = "p2dca21ab5f4ef3ae"
SNAPSHOT = "20260909_212117_Headless_Run_Auto_ge"
N_LEAVES, N_MEMBERS, N_EVAL = 87, 8278, 3445
DIM = 512
TAU = 0.95
CURVE = tuple(round(0.90 + 0.01 * i, 2) for i in range(10))
BAR = 0.10
K = 87
SEEDS = (0, 1, 2, 3, 4)
BOOT_B, BOOT_SEED = 2000, 20261004
DEFF_DECLARED = 1.2
PLAN = dict(n_pairs=150, n_ids=135, p=0.03, se=0.0153, mde=0.043, n_eff=125)
RECORD_IDS = dict(exact=37, norm_v1=70)   # CONTENT-DISJOINT-SPLIT-AUDIT, over ALL generation rows (not tree members)
SCRATCH_PARENT = "E:/TaxoArena_tmp"
OUT_DIR = "E:/TaxoArena_backup_2026-10-04_neardup_audit"
OUTCOME = "neardup_audit_outcome.txt"
DBS = ("mmlu_pro_dataset_cache_v2.db", "embeddings_cache.db", "snapshots.db")
PINS = {"content_closure.py": "1533cb5a56c8e001ddc65d3e2ec0cc4b56aa87e3",
        "flat_mix_mmlu.py": "555ae3ac31b2f27ea040e4bb6a9b20be0eeeecd2"}
PRED = {"P1": (0.00, 0.08), "P2": (0.60, 0.95), "P3": (0.01, 0.04), "P4": (0.00, 0.10)}

VERBATIM = (
    "ND1 (DECIDING; the INTERVAL decides): BLOCK-LOSS = share of the positives PLAIN flags at tau 0.95 that TREE-BLOCK "
    "misses (their twin sits in another leaf); 95% interval by bootstrap over EVAL ids (pairs clustered by EVAL id). "
    "BLOCKS-WELL iff the 95% upper bound <= 0.10; LOSES iff the point > 0.10; UNDETERMINED otherwise. FAILS (rule 8): "
    "BLOCKS-WELL is refuted by a point above 0.10.")
VERBATIM_F = ("F-ND fires iff ND1 reads LOSES: blocking by the tree's leaves loses more than 10% of the twins a plain "
              "threshold finds, so the tree is not a safe blocking index for near-duplicate audits (E3 narrows to 'use "
              "plain ANN'); it also says construction membership and flatLeaf filing disagree for near-identical vectors.")


class Refusal(SystemExit):
    pass


def refuse(msg):
    raise Refusal("%s REFUSED: %s" % (TAG, msg))


# ------------------------------------------------------------------------------------------------ pins
def pins_of_bytes(data):
    data = data.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest(),
                lf16=hashlib.sha256(data).hexdigest()[:16],
                crlf16=hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()[:16])


def pins_of(path):
    with open(path, "rb") as f:
        return pins_of_bytes(f.read())


def fmt_pins(p):
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (p["blob"][:8], p["lf16"], p["crlf16"])


def verify_pin(name, blob=None):
    blob = PINS[name] if blob is None else blob
    got = pins_of(os.path.join(HERE, name))
    if got["blob"] != blob:
        refuse("%s is %s, registered blob:%s (the imported instrument must be the registered one)"
               % (name, fmt_pins(got), blob[:8]))
    return got


verify_pin("content_closure.py")
verify_pin("flat_mix_mmlu.py")
import content_closure as cc  # noqa: E402  (loads split_side by file location)
split_side = cc.split_side
import pool_guard  # noqa: E402


def _kmeans_functions():
    """flat_mix_mmlu.kmeanspp / spherical_kmeans by AST, unchanged, without importing the module (R5)."""
    path = os.path.join(HERE, "flat_mix_mmlu.py")
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    want = {"kmeanspp", "spherical_kmeans"}
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in want]
    consts = [n for n in tree.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Tuple) and any(getattr(e, "id", "") == "K_MAX_ITER" for e in t.elts) or getattr(t, "id", "") == "K_MAX_ITER"
        for t in n.targets)]
    if {n.name for n in body} != want or len(consts) != 1:
        refuse("flat_mix_mmlu.py no longer defines kmeanspp / spherical_kmeans / K_MAX_ITER as pinned")
    ns = {"np": np}
    exec(compile(ast.Module(body=consts + body, type_ignores=[]), path, "exec"), ns)
    return ns["spherical_kmeans"], ns["K_MAX_ITER"]


spherical_kmeans, K_MAX_ITER = _kmeans_functions()


# ------------------------------------------------------------------------------------------------ scratch copies
def copy_inputs(src_root, scratch, out=print):
    """Copy db (+ non-empty -wal) of each DB into scratch; refuse a non-empty -journal or a source that changed."""
    for name in DBS:
        src = os.path.join(src_root, name)
        if not os.path.isfile(src):
            refuse("%s not found (set TAXOARENA_DATA_ROOT to the directory holding the DBs; a worktree has none)" % src)
        j = src + "-journal"
        if os.path.exists(j) and os.path.getsize(j) > 0:
            refuse("%s is non-empty: a writer is active (rule 7); nothing is read" % j)
        wal = src + "-wal"
        has_wal = os.path.exists(wal) and os.path.getsize(wal) > 0
        before = [(os.path.getsize(p), os.path.getmtime(p)) for p in ([src, wal] if has_wal else [src])]
        shutil.copy2(src, os.path.join(scratch, name))
        if has_wal:
            shutil.copy2(wal, os.path.join(scratch, name + "-wal"))
        after = [(os.path.getsize(p), os.path.getmtime(p)) for p in ([src, wal] if has_wal else [src])]
        if before != after:
            refuse("%s changed during the copy (a writer is active; rule 7)" % src)
        if has_wal:   # checkpoint the SCRATCH copy only, so the immutable read sees every committed page
            c = sqlite3.connect(os.path.join(scratch, name))
            c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            c.execute("PRAGMA journal_mode=DELETE")
            c.close()
        out("  copied %s (%d bytes%s) -> scratch" % (name, before[0][0], ", + -wal %d bytes, checkpointed in the copy" % before[1][0] if has_wal else ""))


# ------------------------------------------------------------------------------------------------ loading
def unit_rows(M):
    M = np.asarray(M, dtype=np.float64)
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return M / n


def _vec(blob):
    return np.array(struct.unpack(">%df" % (len(blob) // 4), blob), dtype=np.float64)


def assemble(eval_rows, graph_nodes, query_text, vec_of, options_by_text, n_leaves=N_LEAVES, n_members=N_MEMBERS,
             n_eval=N_EVAL, dim=DIM):
    """Pure assembly (selftest-covered). eval_rows: [(eval_id, stem, options)]; graph_nodes: snapshot node dicts;
    query_text: queryId -> text; vec_of: text -> raw vector; options_by_text: member text -> [options lists]."""
    leaves = sorted((n for n in graph_nodes if not n.get("childIds")), key=lambda n: n["id"])
    if len(leaves) != n_leaves:
        refuse("the snapshot has %d leaves, registered %d" % (len(leaves), n_leaves))
    leaf_ids = [n["id"] for n in leaves]
    listed = defaultdict(dict)   # member queryId -> {leaf index: weight}
    for li, n in enumerate(leaves):
        w = n.get("queryWeights") or {}
        for q in n.get("queryIds") or []:
            listed[q][li] = float(w.get(q, 1.0))
    member_ids = sorted(listed)
    if len(member_ids) != n_members:
        refuse("the leaves list %d distinct TRAIN members, registered %d" % (len(member_ids), n_members))
    miss = [q for q in member_ids if q not in query_text]
    if miss:
        refuse("%d member ids have no embeddings_cache.queries row (e.g. %s)" % (len(miss), miss[:3]))
    member_text = [query_text[q] for q in member_ids]
    eval_rows = sorted(eval_rows, key=lambda r: r[0])
    if len(eval_rows) != n_eval:
        refuse("%d EVAL rows, registered %d" % (len(eval_rows), n_eval))
    no_vec = [t for t in member_text + [r[1] for r in eval_rows] if t not in vec_of]
    if no_vec:
        refuse("%d texts have no embedding" % len(no_vec))
    M = unit_rows([vec_of[t][:dim] for t in member_text])
    E = unit_rows([vec_of[r[1]][:dim] for r in eval_rows])
    member_leaves = [sorted(listed[q]) for q in member_ids]
    ties = 0
    primary = []
    for q in member_ids:
        ws = listed[q]
        top = max(ws.values())
        cands = sorted(li for li, w in ws.items() if w == top)
        ties += len(cands) > 1
        primary.append(cands[0])
    vmf = unit_rows([n["vmfMu"][:dim] if n.get("vmfMu") else np.zeros(dim) for n in leaves])
    return dict(eval_ids=[r[0] for r in eval_rows], eval_text=[r[1] for r in eval_rows], eval_opts=[r[2] for r in eval_rows],
                E=E, member_ids=member_ids, member_text=member_text, M=M, member_leaves=member_leaves, primary=primary,
                primary_ties=ties, leaf_ids=leaf_ids, vmf=vmf, member_opts=[options_by_text.get(t, []) for t in member_text])


def load_real(scratch, out=print):
    pool_guard.DATA_ROOT = scratch
    out("%s pool of record: %s (pool_guard.assert_pool_of_record on the scratch copy of %s)"
        % (TAG, pool_guard.assert_pool_of_record(POOL_ID), DBS[0]))
    ids = pool_guard.eval_ids(POOL_ID)
    con = pool_guard.open_ro(os.path.join(scratch, DBS[0]))
    try:
        link = {q: r for q, r in con.execute("SELECT question_id, mmlu_pro_row_id FROM eval_question_link")}
        rows = {i: (t, o) for i, t, o in con.execute("SELECT id, question, options FROM mmlu_pro")}
    finally:
        con.close()
    bad = [q for q in ids if link.get(q) is None or link[q] not in rows]
    if bad:
        refuse("%d EVAL ids have no linked mmlu_pro row" % len(bad))
    opts = lambda o: [x if isinstance(x, str) else json.dumps(x, sort_keys=True) for x in (json.loads(o) if o else [])]
    eval_rows = [(q, rows[link[q]][0], opts(rows[link[q]][1])) for q in ids]
    options_by_text = defaultdict(list)
    for t, o in rows.values():
        options_by_text[t].append(opts(o))
    con = pool_guard.open_ro(os.path.join(scratch, DBS[2]))
    try:
        row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (SNAPSHOT,)).fetchone()
    finally:
        con.close()
    if row is None:
        refuse("snapshot %s not in snapshots.db" % SNAPSHOT)
    graph_sha = hashlib.sha256(row[0].encode("utf-8")).hexdigest()
    g = json.loads(row[0])
    nodes = g["nodes"] if isinstance(g["nodes"], list) else list(g["nodes"].values())
    qids = sorted({q for n in nodes if not n.get("childIds") for q in (n.get("queryIds") or [])})
    con = pool_guard.open_ro(os.path.join(scratch, DBS[1]))
    try:
        query_text = {}
        for s in range(0, len(qids), 500):
            ch = qids[s:s + 500]
            for q, t in con.execute("SELECT id, raw_text FROM queries WHERE id IN (%s)" % ",".join("?" * len(ch)), ch):
                query_text[q] = t
        want = set(query_text.values()) | {r[1] for r in eval_rows}
        vec_of, h = {}, hashlib.sha256()
        for t, blob in con.execute("SELECT query, vector FROM embeddings"):
            if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
                vec_of[t] = _vec(blob)
    finally:
        con.close()
    bad_hash = [q for q, t in query_text.items() if "q_" + hashlib.sha256(t.encode("utf-8")).hexdigest()[:16] != q]
    if bad_hash:
        refuse("%d member ids do not equal 'q_' + sha256(raw_text)[:16]" % len(bad_hash))
    for t in sorted(vec_of):
        h.update(t.encode("utf-8") + b"\x1f" + vec_of[t].astype(">f4").tobytes())
    d = assemble(eval_rows, nodes, query_text, vec_of, options_by_text)
    full = [len(vec_of[t]) for t in d["member_text"][:1]]
    d["pins"] = dict(graph_sha256=graph_sha, vectors_sha256=h.hexdigest(), n_vectors=len(vec_of), full_dim=full[0],
                     eval_set_sha256=hashlib.sha256("\n".join("%d\x1f%s" % (q, t) for q, t in zip(d["eval_ids"], d["eval_text"])).encode("utf-8")).hexdigest(),
                     member_set_sha256=hashlib.sha256("\n".join("%s\x1f%s" % (q, t) for q, t in zip(d["member_ids"], d["member_text"])).encode("utf-8")).hexdigest())
    return d


# ------------------------------------------------------------------------------------------------ positives (no cosine)
def positives(d):
    """[(eval index, member index, tier)] sharing a CK-CLOSE-v1 key; computed from texts only."""
    by_key = defaultdict(list)
    for j, t in enumerate(d["member_text"]):
        by_key[cc.ck_key(t)].append(j)
    out = []
    for i, (t, o) in enumerate(zip(d["eval_text"], d["eval_opts"])):
        for j in by_key.get(cc.ck_key(t), ()):
            mt = d["member_text"][j]
            if mt == t:
                tier = "EXACT"
            elif any(split_side.content_key(mt, mo, "") == split_side.content_key(t, o, "") for mo in d["member_opts"][j]):
                tier = "SAME-OPTIONS"
            else:
                tier = "STEM-ONLY"
            out.append((i, j, tier))
    return out


def kish(sizes):
    sizes = list(sizes)
    return sum(s * s for s in sizes) / sum(sizes) if sizes else float("nan")


# ------------------------------------------------------------------------------------------------ the readout
def nd1_verdict(point, lo, hi):
    if point > BAR:
        return "LOSES"
    if hi <= BAR:
        return "BLOCKS-WELL"
    return "UNDETERMINED"


def in_interval(v, key):
    lo, hi = PRED[key]
    return bool(lo <= v <= hi)


def cluster_boot(eidx, miss, B=BOOT_B, seed=BOOT_SEED):
    """Percentile 95% interval of sum(miss)/n, resampling EVAL ids (clusters) with replacement; also var_boot."""
    cl = defaultdict(lambda: [0, 0])
    for i, m in zip(eidx, miss):
        cl[i][0] += int(m); cl[i][1] += 1
    keys = sorted(cl)
    a = np.array([cl[k][0] for k in keys], dtype=np.float64)
    n = np.array([cl[k][1] for k in keys], dtype=np.float64)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(keys), size=(B, len(keys)))
    stats = a[idx].sum(axis=1) / n[idx].sum(axis=1)
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5)), float(stats.var(ddof=1)), [int(x) for x in n]


def cp_upper(x, n):
    """Exact two-sided 95% Clopper-Pearson upper bound on x / n: Beta(0.975; x + 1, n - x); 1 when x == n."""
    from scipy.stats import beta
    if n <= 0:
        return float("nan")
    return 1.0 if x >= n else float(beta.ppf(0.975, x + 1, n - x))


def file_leaf(E, C):
    return np.argmax(E @ C.T, axis=1)


def analyze(d, pos, out=print, k=None, seeds=SEEDS):
    E, M = d["E"], d["M"]
    nE, nM, nL = E.shape[0], M.shape[0], len(d["leaf_ids"])
    k = nL if k is None else k
    # R2 centroids: unit mean of each leaf's listed members
    mem = np.zeros((nM, nL), dtype=bool)
    for j, ls in enumerate(d["member_leaves"]):
        mem[j, ls] = True
    C = unit_rows(mem.T.astype(np.float64) @ M)
    filed = file_leaf(E, C)
    filed_vmf = file_leaf(E, d["vmf"])
    S = E @ M.T
    pe = np.array([p[0] for p in pos], dtype=np.int64)
    pm = np.array([p[1] for p in pos], dtype=np.int64)
    ps = S[pe, pm] if len(pos) else np.zeros(0)
    in_block = mem[pm, filed[pe]] if len(pos) else np.zeros(0, dtype=bool)
    prim = np.array(d["primary"], dtype=np.int64)
    in_prim = (prim[pm] == filed[pe]) if len(pos) else np.zeros(0, dtype=bool)
    # k-means arm
    km = []
    for s in seeds:
        r = spherical_kmeans(M, k, s)
        lab = np.asarray(r["labels"])
        ef = np.argmax(E @ r["centers"].T, axis=1)
        km.append(dict(seed=s, labels=lab, efile=ef, iters=r["iters"], converged=bool(r["converged"]),
                       sizes=np.bincount(lab, minlength=k)))

    def arm_at(tau):
        flag = ps >= tau
        nflag = int(flag.sum())
        tree_hit = flag & in_block
        loss = (nflag - int(tree_hit.sum())) / nflag if nflag else float("nan")
        prim_loss = (nflag - int((flag & in_prim).sum())) / nflag if nflag else float("nan")
        km_loss = []
        for r in km:
            hit = flag & (r["labels"][pm] == r["efile"][pe]) if len(pos) else flag
            km_loss.append((nflag - int(hit.sum())) / nflag if nflag else float("nan"))
        allflag = S >= tau
        n_plain = int(allflag.sum())
        n_tree = int((allflag & mem[:, filed].T).sum())
        n_km = [int((allflag & (r["labels"][None, :] == r["efile"][:, None])).sum()) for r in km]
        npos = len(pos)
        return dict(tau=tau, nflag=nflag, loss=loss, prim_loss=prim_loss, km_loss=km_loss,
                    km_mean=float(np.mean(km_loss)) if nflag else float("nan"),
                    rec_plain=nflag / npos if npos else float("nan"),
                    rec_tree=int(tree_hit.sum()) / npos if npos else float("nan"),
                    rec_km=[(nflag - kl * nflag) / npos for kl in km_loss] if nflag else [],
                    prec_plain=nflag / n_plain if n_plain else float("nan"),
                    prec_tree=int(tree_hit.sum()) / n_tree if n_tree else float("nan"),
                    prec_km=[(nflag - kl * nflag) / nk if nk else float("nan") for kl, nk in zip(km_loss, n_km)] if nflag else [],
                    n_plain=n_plain, n_tree=n_tree, n_km=n_km)

    main_arm = arm_at(TAU)
    flag = ps >= TAU
    dec_e = pe[flag]
    dec_miss = ~in_block[flag]
    if main_arm["nflag"] == 0:
        refuse("no positive pair is flagged by PLAIN at tau %.2f: ND1 has no object (R3); nothing is written" % TAU)
    lo, hi, vboot, csizes = cluster_boot(dec_e, dec_miss)
    p = main_arm["loss"]
    n_miss = int(dec_miss.sum())
    cp_hi = cp_upper(n_miss, int(flag.sum()))
    degenerate = bool(hi == lo)                       # C-2: a zero-width bootstrap interval (e.g. 0 misses -> [0, 0])
    hi_decide = cp_hi if degenerate else hi
    p_lo, p_hi, _, _ = cluster_boot(dec_e, ~in_prim[flag])   # C-1: the primary-leaf-only interval, same bootstrap
    p_point = main_arm["prim_loss"]
    leaf_size = mem.sum(axis=0)
    frac_eval = float(leaf_size[filed].mean() / nM)
    frac_unw = float(leaf_size.mean() / nM)
    km_frac = [float(r["sizes"][r["efile"]].mean() / nM) for r in km]
    mem_self = file_leaf(M, C)
    consistent = float(np.mean([mem_self[j] in d["member_leaves"][j] for j in range(nM)]))
    n_dec = int(flag.sum())
    m_dec = kish(csizes)
    m_all = kish(Counter(pe.tolist()).values())
    deff_boot = vboot / (p * (1 - p) / n_dec) if 0 < p < 1 else None
    res = dict(nE=nE, nM=nM, nL=nL, k=k, npos=len(pos), pos_ids=len(set(pe.tolist())),
               tiers=Counter(t for _, _, t in pos), tier_ids={t: len({i for i, _, tt in pos if tt == t}) for t in ("EXACT", "SAME-OPTIONS", "STEM-ONLY")},
               main=main_arm, curve=[arm_at(t) for t in CURVE], lo=lo, hi=hi, verdict=nd1_verdict(p, lo, hi_decide),
               cp_hi=cp_hi, degenerate=degenerate, hi_decide=hi_decide, n_miss=n_miss,
               verdict_boot=nd1_verdict(p, lo, hi), verdict_cp=nd1_verdict(p, lo, cp_hi),
               prim_lo=p_lo, prim_hi=p_hi, prim_verdict=nd1_verdict(p_point, p_lo, cp_upper(int((~in_prim[flag]).sum()), int(flag.sum())) if p_hi == p_lo else p_hi),
               n_dec=n_dec, dec_ids=len(csizes), csizes=Counter(csizes), m_dec=m_dec, m_all=m_all, deff_boot=deff_boot,
               frac_eval=frac_eval, frac_unw=frac_unw, km_frac=km_frac, consistent=consistent,
               filing_agree_vmf=float(np.mean(filed == filed_vmf)),
               cos_vmf=[float(x) for x in np.sum(C * d["vmf"], axis=1)], km=[dict(seed=r["seed"], iters=r["iters"], converged=r["converged"]) for r in km],
               primary_ties=d["primary_ties"], multi=sum(1 for ls in d["member_leaves"] if len(ls) > 1),
               tier_loss={t: (int(sum(1 for (i, j, tt), f, b in zip(pos, ps >= TAU, in_block) if tt == t and f and not b)),
                              int(sum(1 for (i, j, tt), f in zip(pos, ps >= TAU) if tt == t and f))) for t in ("EXACT", "SAME-OPTIONS", "STEM-ONLY")})
    return res


def f3(x):
    return "n/a" if x is None or (isinstance(x, float) and x != x) else "%.3f" % x


def render(res, pins_lines, out=print):
    m = res["main"]
    L = []
    w = L.append
    w("%s %s readout (zero calls); tree bareq512_s42 snapshot %s; pool %s" % (TAG, TEST_ID, SNAPSHOT, POOL_ID))
    w("PINS:")
    L.extend("  " + s for s in pins_lines)
    w("DENOMINATORS: EVAL items %d; TRAIN members %d; leaves %d; all (EVAL, member) pairs %d" % (res["nE"], res["nM"], res["nL"], res["nE"] * res["nM"]))
    w("POSITIVES (CK-CLOSE-v1 stem_key twin pairs): %d pairs over %d EVAL ids; tiers (pairs / EVAL ids) EXACT %d / %d, SAME-OPTIONS %d / %d, STEM-ONLY %d / %d"
      " [record over ALL generation rows, not tree members: exact %d ids, norm-v1 %d ids]"
      % (res["npos"], res["pos_ids"], res["tiers"]["EXACT"], res["tier_ids"]["EXACT"], res["tiers"]["SAME-OPTIONS"], res["tier_ids"]["SAME-OPTIONS"],
         res["tiers"]["STEM-ONLY"], res["tier_ids"]["STEM-ONLY"], RECORD_IDS["exact"], RECORD_IDS["norm_v1"]))
    w("READINGS: R1 block = the leaf's listed members (%d members listed in >1 leaf; primary ties %d); R2 centroid = unit mean of listed members"
      " (cos to vmfMu min %.4f, median %.4f; filing agreement with vmfMu filing %.4f); members filing into a leaf that lists them %.4f"
      % (res["multi"], res["primary_ties"], min(res["cos_vmf"]), float(np.median(res["cos_vmf"])), res["filing_agree_vmf"], res["consistent"]))
    w("CRITERION ND1 (verbatim): " + VERBATIM)
    w("ND1 DENOMINATOR: positives PLAIN flags at tau %.2f = %d pairs over %d EVAL ids (of %d positive pairs)" % (TAU, res["n_dec"], res["dec_ids"], res["npos"]))
    w("ND1 BLOCK-LOSS = %s [95%% %s, %s] (TREE-BLOCK misses %d of %d; bootstrap over EVAL ids, B %d, seed %d)"
      % (f3(m["loss"]), f3(res["lo"]), f3(res["hi"]), int(round(m["loss"] * m["nflag"])), m["nflag"], BOOT_B, BOOT_SEED))
    w("ND1 CLOPPER-PEARSON 95%% upper (exact, pairs; valid as an exact bound only at Kish m 1.000, here %.3f): %s; bootstrap upper %s"
      % (res["m_dec"], f3(res["cp_hi"]), f3(res["hi"])))
    w("ND1 DECIDING UPPER BOUND (C-2 rule, READY_neardup_audit; a builder rule FLAGGED FOR THE REGISTRAR): %s = %s"
      % ("CLOPPER-PEARSON (the bootstrap interval is degenerate, zero width)" if res["degenerate"] else "BOOTSTRAP (registered; CP printed beside)",
         f3(res["hi_decide"])))
    w("ND1 bootstrap-only verdict %s; CP-upper verdict %s; %s" % (res["verdict_boot"], res["verdict_cp"],
      "THE TWO DIFFER (named)" if res["verdict_boot"] != res["verdict_cp"] else "the two agree"))
    w("ND1 VERDICT: %s" % res["verdict"])
    if res["verdict"] == "BLOCKS-WELL":
        w("ND1 FAILS-rule: not refuted (point %s <= %.2f)" % (f3(m["loss"]), BAR))
    else:
        w("ND1 FAILS-rule: BLOCKS-WELL not read; %s" % ("point %s > %.2f" % (f3(m["loss"]), BAR) if res["verdict"] == "LOSES" else "upper bound %s > %.2f" % (f3(res["hi_decide"]), BAR)))
    fired = bool(res["verdict"] == "LOSES")
    w("FALSIFIER F-ND (verbatim): " + VERBATIM_F)
    w("F-ND: %s" % ("FIRED (ND1 LOSES): the tree is not a safe blocking index; E3 narrows to 'use plain ANN'" if fired else "NOT FIRED (ND1 %s)" % res["verdict"]))
    w("SENSITIVITY (R1): primary-leaf-only block BLOCK-LOSS %s [95%% %s, %s] -> %s; %s" % (
        f3(m["prim_loss"]), f3(res["prim_lo"]), f3(res["prim_hi"]), res["prim_verdict"],
        "R1-DEPENDENT (differs from the ND1 verdict)" if res["prim_verdict"] != res["verdict"] else "same verdict as ND1"))
    for t in ("EXACT", "SAME-OPTIONS", "STEM-ONLY"):
        a, b = res["tier_loss"][t]
        w("TIER %s: tree misses %d of %d PLAIN-flagged" % (t, a, b))
    w("SUPPORT: declared DEFF %.1f (pilot assumption; planning n %d pairs / %d ids, SE %.4f, MDE80 %.3f, n_eff %d)"
      % (DEFF_DECLARED, PLAN["n_pairs"], PLAN["n_ids"], PLAN["se"], PLAN["mde"], PLAN["n_eff"]))
    deff = res["m_dec"]
    pse = res["main"]["loss"]
    se_real = (pse * (1 - pse) * deff / res["n_dec"]) ** 0.5
    se_plan = (PLAN["p"] * (1 - PLAN["p"]) * deff / res["n_dec"]) ** 0.5
    w("SUPPORT MEASURED: deciding pairs %d over %d EVAL ids, cluster sizes %s; Kish m (DEFF at rho=1, upper bound) %.3f vs declared %.1f;"
      " Kish m over all positives %.3f; bootstrap variance ratio %s; n_eff %.1f; realised SE %.4f (MDE80 %.3f); SE at the planning 0.03 %.4f (MDE80 %.3f)"
      % (res["n_dec"], res["dec_ids"], "/".join("%d:%d" % (s, res["csizes"][s]) for s in sorted(res["csizes"])), deff, DEFF_DECLARED,
         res["m_all"], f3(res["deff_boot"]), res["n_dec"] / deff, se_real, 2.8 * se_real, se_plan, 2.8 * se_plan))
    w("SUPPORT: no judge direction is scored, so wrong(established) and the two tie conventions have no object here")
    w("ARMS at tau %.2f: PLAIN recall %s precision(LB) %s flagged %d; TREE-BLOCK recall %s precision(LB) %s flagged %d;"
      " KMEANS-BLOCK (k %d, seeds %s) BLOCK-LOSS %s (per seed %s) recall %s precision(LB) %s"
      % (TAU, f3(m["rec_plain"]), f3(m["prec_plain"]), m["n_plain"], f3(m["rec_tree"]), f3(m["prec_tree"]), m["n_tree"], res["k"],
         ",".join(str(r["seed"]) for r in res["km"]), f3(m["km_mean"]), "/".join(f3(x) for x in m["km_loss"]),
         f3(float(np.mean(m["rec_km"])) if m["rec_km"] else None), f3(float(np.nanmean(m["prec_km"])) if m["prec_km"] else None)))
    w("KMEANS fits: %s" % "; ".join("seed %d iters %d converged %s" % (r["seed"], r["iters"], r["converged"]) for r in res["km"]))
    w("TREE minus KMEANS BLOCK-LOSS [AN]: %+.3f (descriptive; the anchored tree carries label information)" % (m["loss"] - m["km_mean"]))
    w("COMPARISON FRACTION: registered (mean leaf size / %d, unweighted; scores P3) %.4f; R4 reading (EVAL-weighted, descriptive) %.4f; KMEANS EVAL-weighted %s"
      % (res["nM"], res["frac_unw"], res["frac_eval"], "/".join("%.4f" % x for x in res["km_frac"])))
    w("CURVE tau: PLAIN recall / TREE BLOCK-LOSS / KMEANS BLOCK-LOSS (mean) / PLAIN precision(LB) / TREE precision(LB)")
    for c in res["curve"]:
        w("  tau %.2f: %s / %s / %s / %s / %s (flagged positives %d)" % (c["tau"], f3(c["rec_plain"]), f3(c["loss"]), f3(c["km_mean"]),
                                                                        f3(c["prec_plain"]), f3(c["prec_tree"]), c["nflag"]))
    preds = [("P1", "BLOCK-LOSS 0.03 [0.00, 0.08]", m["loss"]), ("P2", "PLAIN recall at tau 0.95 0.80 [0.60, 0.95]", m["rec_plain"]),
             ("P3", "comparison fraction 0.02 [0.01, 0.04]", res["frac_unw"]), ("P4", "KMEANS-BLOCK BLOCK-LOSS 0.03 [0.00, 0.10] (descriptive)", m["km_mean"])]
    for key, text, v in preds:
        w("PREDICTION %s (%s): value %s -> %s" % (key, text, f3(v), "HELD" if in_interval(v, key) else "FAILED"))
    w("PREDICTION P1 verdict odds (BLOCKS-WELL 0.65, UNDETERMINED 0.20, LOSES 0.15): read %s" % res["verdict"])
    w("NOT SHOWN: tree over k-means or ANN as an index ([AN]); paraphrase detection beyond stem_key (precision is a LOWER bound);"
      " anything about the content-closed v2 split; a decontamination verdict for any judged result")
    for s in L:
        out(s)
    return L


# ------------------------------------------------------------------------------------------------ outputs
def write_once(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        refuse("%s exists: outcome files are write-once (nothing overwritten)" % path)


def write_outputs(out_dir, lines, out=print):
    path = os.path.join(out_dir, OUTCOME)
    sums = os.path.join(out_dir, "SHA256SUMS.txt")
    if os.path.exists(path) or os.path.exists(sums):
        refuse("%s already holds an outcome: write-once (nothing overwritten)" % out_dir)
    text = "\n".join(lines) + "\n"
    write_once(path, text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    write_once(sums, "%s  %s\n" % (sha, OUTCOME))
    out("%s wrote %s (sha256 %s) and SHA256SUMS.txt (write-once; never committed)" % (TAG, path, sha))
    return path, sha


# ------------------------------------------------------------------------------------------------ entry
def script_pin_lines(d):
    me = pins_of(os.path.abspath(__file__))
    lines = ["neardup_audit.py %s (LF of record; CRLF beside)" % fmt_pins(me),
             "content_closure.py %s (registered blob 1533cb5a, verified)" % fmt_pins(pins_of(os.path.join(HERE, "content_closure.py"))),
             "flat_mix_mmlu.py %s (k-means source by AST, verified; K_MAX_ITER %d)" % (fmt_pins(pins_of(os.path.join(HERE, "flat_mix_mmlu.py"))), K_MAX_ITER),
             "split_side.py %s (%s)" % (fmt_pins(pins_of(os.path.join(HERE, "split_side.py"))), cc.KEY_NAME),
             "pool_guard.py %s" % fmt_pins(pins_of(os.path.join(HERE, "pool_guard.py")))]
    p = d.get("pins")
    if p:
        lines += ["snapshot graph sha256 %s" % p["graph_sha256"],
                  "vectors used sha256 %s (%d texts, full dim %d, sliced %d)" % (p["vectors_sha256"], p["n_vectors"], p["full_dim"], DIM),
                  "EVAL set sha256 %s; member set sha256 %s" % (p["eval_set_sha256"], p["member_set_sha256"])]
    return lines


def main(argv=None, loader=None, out=print, out_dir=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    out_dir = a.out_dir or out_dir or OUT_DIR
    if a.run and (os.path.exists(os.path.join(out_dir, OUTCOME)) or os.path.exists(os.path.join(out_dir, "SHA256SUMS.txt"))):
        refuse("%s already holds an outcome: write-once (nothing overwritten, nothing computed)" % out_dir)
    scratch = None
    try:
        if loader is None:
            os.makedirs(SCRATCH_PARENT, exist_ok=True)
            scratch = tempfile.mkdtemp(prefix="neardup_", dir=SCRATCH_PARENT)
            copy_inputs(SRC_ROOT, scratch, out=lambda s: None)
            d = load_real(scratch, out=out)
            out("  inputs: %s copied from %s into scratch %s (removed at exit)" % (", ".join(DBS), SRC_ROOT, scratch))
        else:
            d = loader(out)
        pos = positives(d)
        out("%s positives (CK-CLOSE-v1 stem_key twin pairs, before any cosine): %d pairs over %d EVAL ids"
            % (TAG, len(pos), len({p[0] for p in pos})))
        if not pos:
            refuse("no stem_key twin pair between the EVAL ids and the TRAIN members: ND1 has no positives")
        if a.dry_run:
            for s in script_pin_lines(d):
                out("  PIN " + s)
            tiers = Counter(t for _, _, t in pos)
            n_ids = len({p[0] for p in pos})
            sizes = Counter(p[0] for p in pos).values()
            mk = kish(sizes)
            se = (PLAN["p"] * (1 - PLAN["p"]) * mk / len(pos)) ** 0.5
            out("  DENOMINATORS: EVAL items %d; TRAIN members %d; leaves %d; pairs %d; positives %d pairs / %d EVAL ids (EXACT %d, SAME-OPTIONS %d, STEM-ONLY %d)"
                % (len(d["eval_ids"]), len(d["member_ids"]), len(d["leaf_ids"]), len(d["eval_ids"]) * len(d["member_ids"]), len(pos), n_ids,
                   tiers["EXACT"], tiers["SAME-OPTIONS"], tiers["STEM-ONLY"]))
            out("  SUPPORT (pre-cosine, all positives; the deciding subset is the PLAIN-flagged part, known only at --run): Kish m %.3f vs declared DEFF %.1f;"
                " SE at the planning 0.03 with this m %.4f (MDE80 %.3f) vs registered %.4f (%.3f)" % (mk, DEFF_DECLARED, se, 2.8 * se, PLAN["se"], PLAN["mde"]))
            out("%s DRY-RUN: no cosine read, nothing written; tau %.2f, bar %.2f, B %d, k %d, seeds %s; outcome would go to %s"
                % (TAG, TAU, BAR, BOOT_B, K, ",".join(map(str, SEEDS)), os.path.join(out_dir, OUTCOME)))
            return 0
        res = analyze(d, pos, out=out)
        lines = render(res, script_pin_lines(d) + ["run date %s" % datetime.date.today().isoformat()], out=out)
        write_outputs(out_dir, lines, out=out)
        return 0
    finally:
        if scratch is not None:
            shutil.rmtree(scratch, ignore_errors=True)
            out("  scratch %s removed: %s" % (scratch, not os.path.exists(scratch)))


# ------------------------------------------------------------------------------------------------ selftest
def _fixture(n_leaves=50, per_leaf=20, n_exact=40, n_boundary=0, n_sub=0, n_near=0, multi=False, cluster3=False,
             fold_twins=0, rotate_vmf=True, unequal=False, sub_cos=0.92, big_cluster=0):
    """Synthetic data with a known answer. Leaves are orthogonal directions e_l; members e_l + small noise. EXACT twins:
    the EVAL text equals a member's text and shares its vector (never a tree miss). BOUNDARY twins: the member (text
    'B... X') listed in leaf 1 near the e0/e1 bisector, the EVAL ('b... x', same stem_key) just on the leaf-0 side, cos
    ~0.995: a miss for TREE and KMEANS. SUB twins: same stem_key, cos ~sub_cos < 0.95, the member in ANOTHER leaf: never in
    the ND1 denominator, and a tree miss at tau 0.90. NEAR: cos >= 0.95, different stems (precision only)."""
    rng = np.random.default_rng(7)
    dim = max(64, n_leaves + 4)
    sizes = [per_leaf] * n_leaves
    if unequal:
        sizes[0] = per_leaf * 6
    vec_of, mtext, nodes, qtext = {}, [], [], {}
    leaf_members = defaultdict(list)
    weights = defaultdict(dict)

    def add_member(text, v, leaves, w=None):
        q = "q_" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        qtext[q] = text; vec_of[text] = v
        for li, l in enumerate(leaves):
            leaf_members[l].append(q); weights[l][q] = (w[li] if w else 1.0)
        return q

    e = np.eye(dim)
    for l in range(n_leaves):
        for m in range(sizes[l]):
            add_member("member %d of leaf %d" % (m, l), e[l] + 0.02 * rng.standard_normal(dim), [l])
    evals = []
    eid = 1
    for t in range(n_exact):   # exact twins: EVAL text == member text "member t%m of leaf l"
        l = 2 + (t % (n_leaves - 2)) if n_leaves > 2 else t % n_leaves
        if unequal:
            l = 0
        txt = "member %d of leaf %d" % (t // max(1, n_leaves - 2) % sizes[l], l)
        evals.append((eid, txt, ["a", "b"])); eid += 1
    for t in range(n_boundary):   # leaf pairs (42, 43), (44, 45), (46, 47), (48, 49): at most 2 per leaf
        a, b = n_leaves - 8 + 2 * (t % 4), n_leaves - 7 + 2 * (t % 4)
        mid = (e[a] + e[b]) / np.sqrt(2)
        vm = mid - 0.04 * (e[a] - e[b]) + 0.001 * t * e[dim - 1]
        ve = mid + 0.04 * (e[a] - e[b]) + 0.001 * t * e[dim - 1]
        add_member("Boundary  Question %d X" % t, vm, [b])
        evals.append((eid, "boundary question %d x" % t, ["a", "b"])); vec_of["boundary question %d x" % t] = ve; eid += 1
    for t in range(n_sub):
        l, l2 = 2 + t % max(1, n_leaves - 3), 3 + t % max(1, n_leaves - 3)
        ang = np.arccos(sub_cos)
        vm = np.cos(ang / 2) * e[l] + np.sin(ang / 2) * e[dim - 2]
        ve = np.cos(ang / 2) * e[l] - np.sin(ang / 2) * e[dim - 2]
        add_member("Sub Twin %d" % t, vm, [l2 if n_leaves > 3 else l])
        evals.append((eid, "sub twin %d" % t, ["a", "b"])); vec_of["sub twin %d" % t] = ve; eid += 1
    for t in range(n_near):
        l = 2 + t % max(1, n_leaves - 2)
        add_member("near member %d" % t, e[l] + 0.001 * e[dim - 3], [l])
        evals.append((eid, "unrelated eval %d" % t, ["a"])); vec_of["unrelated eval %d" % t] = e[l]; eid += 1
    for mm in range(int(multi)):   # member listed in leaves 3 (weight 0.6, primary) and 2; vector in leaf 2; EVAL twin files to 2
        nm = "Multi Leaf Twin" + ("" if mm == 0 else " %d" % mm)
        v = e[2] + 0.001 * (mm + 1) * e[dim - 4]
        add_member(nm, v, [3, 2], w=[0.6, 0.4])
        evals.append((eid, nm.lower(), ["a", "b"])); vec_of[nm.lower()] = v; eid += 1
    if cluster3:   # one EVAL id with 3 stem-twin members (all exact-vector copies in leaf 2)
        for c in range(3):
            add_member("Triple Twin" + " " * (c + 1), e[2] + 0.0005 * (c + 1) * e[dim - 5], [2])
        evals.append((eid, "triple twin", ["a", "b"])); vec_of["triple twin"] = e[2] + 0.0005 * e[dim - 5]; eid += 1
    for t in range(fold_twins):   # case / whitespace twins of exact members: stem_key equal, text unequal, same vector, OTHER options (STEM-ONLY)
        l = 2 + t % max(1, n_leaves - 2)
        txt = "member %d of leaf %d" % (per_leaf - 1, l)
        v = vec_of[txt]
        evals.append((eid, "MEMBER  %d of LEAF %d" % (per_leaf - 1, l), ["c", "d"])); vec_of["MEMBER  %d of LEAF %d" % (per_leaf - 1, l)] = v; eid += 1
    if big_cluster:   # one EVAL id with big_cluster twins whose vectors sit at e0 but are LISTED in leaf 1 (all tree misses)
        for c in range(big_cluster):
            add_member("Big Cluster" + " " * (c + 1), e[0] + 0.0003 * (c + 1) * e[dim - 6], [1])
        vec_of["big cluster"] = e[0] + 0.0003 * e[dim - 6]
        evals.append((eid, "big cluster", ["a"])); eid += 1
    for l in range(n_leaves):
        mu = e[(l + 1) % n_leaves] if rotate_vmf else e[l]
        nodes.append(dict(id="n%05d" % l, childIds=[], queryIds=leaf_members[l], queryWeights=weights[l], vmfMu=list(mu)))
    nodes.append(dict(id="root", childIds=["n%05d" % l for l in range(n_leaves)], queryIds=[]))
    opts_by_text = {t: [["a", "b"]] for t in qtext.values()}
    n_mem = len(qtext)

    def loader(out):
        d = assemble(evals, nodes, qtext, vec_of, opts_by_text, n_leaves=n_leaves, n_members=n_mem, n_eval=len(evals), dim=dim)
        d["pins"] = None
        return d
    return loader, evals, nodes, qtext, vec_of


def selftest():
    import io
    import contextlib
    fails = []
    ok = lambda c, label: (print(("  ok   " if c else "  FAIL ") + label), None if c else fails.append(label))

    def run(loader, args=("--run",)):
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT if os.path.isdir(SCRATCH_PARENT) else None) as td:
            buf = []
            try:
                rc = main(list(args) + ["--out-dir", td], loader=loader, out=buf.append)
            except Refusal as r:
                return str(r), buf, None
            text = None
            p = os.path.join(td, OUTCOME)
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    text = f.read()
            return rc, buf, text

    def line(buf, prefix):
        hits = [s for s in buf if s.startswith(prefix)]
        return hits[0] if hits else ""

    # verdict table (unit) incl. both boundaries
    for args, want in (((0.05, 0.0, 0.10), "BLOCKS-WELL"), ((0.10, 0.02, 0.18), "UNDETERMINED"), ((0.1001, 0.05, 0.2), "LOSES"),
                       ((0.05, 0.0, 0.1001), "UNDETERMINED")):
        ok(nd1_verdict(*args) == want, "nd1_verdict%s == %s" % (args, want))

    # F1: 40 exact + 10 sub-threshold twins + multi-leaf + triple cluster + 4 near non-twins + 2 fold twins
    ld, *_ = _fixture(n_exact=40, n_sub=10, n_near=4, multi=True, cluster3=True, fold_twins=2)
    rc, buf, text = run(ld)
    ok(rc == 0 and text is not None, "F1 --run returns 0 and writes the outcome")
    ok("positives (CK-CLOSE-v1 stem_key twin pairs, before any cosine): 56 pairs over 54 EVAL ids" in "\n".join(buf),
       "F1 positives 56 pairs / 54 ids (40 exact + 10 sub + 1 multi + 3 triple (one id) + 2 case/whitespace; stem_key, not exact text)")
    ok(line(buf, "ND1 DENOMINATOR").startswith("ND1 DENOMINATOR: positives PLAIN flags at tau 0.95 = 46 pairs over 44 EVAL ids"),
       "F1 denominator = PLAIN-flagged positives only (46 of 56; the 10 sub-threshold twins excluded)")
    ok(line(buf, "ND1 BLOCK-LOSS").startswith("ND1 BLOCK-LOSS = 0.000 [95% 0.000, 0.000] (TREE-BLOCK misses 0 of 46"), "F1 BLOCK-LOSS 0.000 [0.000, 0.000]")
    ok(line(buf, "ND1 VERDICT") == "ND1 VERDICT: BLOCKS-WELL", "F1 verdict BLOCKS-WELL")
    ok(line(buf, "F-ND: ") == "F-ND: NOT FIRED (ND1 BLOCKS-WELL)", "F1 F-ND NOT FIRED line printed")
    ok(line(buf, "ND1 FAILS-rule") == "ND1 FAILS-rule: not refuted (point 0.000 <= 0.10)", "F1 FAILS-rule line")
    ok(line(buf, "SENSITIVITY (R1)") == "SENSITIVITY (R1): primary-leaf-only block BLOCK-LOSS 0.022 [95% 0.000, 0.068] -> BLOCKS-WELL; same verdict as ND1",
       "F1 primary-only sensitivity 1/46 = 0.022 with its interval and verdict (C-1)")
    ok(line(buf, "ND1 CLOPPER-PEARSON").endswith(": 0.077; bootstrap upper 0.000") and "CLOPPER-PEARSON (the bootstrap interval is degenerate, zero width) = 0.077" in line(buf, "ND1 DECIDING UPPER"),
       "F1 0/46: bootstrap degenerate, CP upper 1 - 0.025^(1/46) = 0.077 decides (C-2)")
    ok("Kish m (DEFF at rho=1, upper bound) 1.130 vs declared 1.2" in line(buf, "SUPPORT MEASURED"),
       "F1 Kish m of the deciding pairs = (43 + 9)/46 = 1.130")
    ok("Kish m over all positives 1.107" in line(buf, "SUPPORT MEASURED"), "F1 Kish m over all positives (53 + 9)/56 = 1.107")
    ok(line(buf, "PREDICTION P1").endswith("value 0.000 -> HELD"), "F1 P1 HELD")
    ok(line(buf, "PREDICTION P2").endswith("value 0.821 -> HELD"), "F1 P2 PLAIN recall 46/56 = 0.821 HELD")
    ok(line(buf, "PREDICTION P3").endswith("value 0.020 -> HELD") and "registered (mean leaf size / 1018, unweighted; scores P3) 0.0200; R4 reading (EVAL-weighted, descriptive) 0.0208" in line(buf, "COMPARISON FRACTION"),
       "F1 P3 scored on the registered unweighted 0.0200 (HELD), EVAL-weighted 0.0208 beside (C-3)")
    ok(line(buf, "PREDICTION P4").endswith("value 0.000 -> HELD"), "F1 P4 HELD")
    ok("seeds 0,1,2,3,4" in line(buf, "ARMS at tau"), "F1 k-means seeds 0-4 printed")
    ok("  tau 0.90: 1.000 / 0.179 /" in "\n".join(buf), "F1 curve at tau 0.90: recall 1.000, tree loss 10/56 = 0.179 (sub twins listed in another leaf)")
    alltext = "\n".join(buf)
    ok("TIER EXACT: tree misses 0 of 40" in alltext and "TIER SAME-OPTIONS: tree misses 0 of 4" in alltext and "TIER STEM-ONLY: tree misses 0 of 2" in alltext,
       "F1 tiers EXACT 40 / SAME-OPTIONS 4 (multi + triple) / STEM-ONLY 2 (case twins with other options)")
    ok(text is not None and "ND1 VERDICT: BLOCKS-WELL" in text and "PREDICTION P4" in text and "F-ND: NOT FIRED" in text, "F1 outcome file carries verdict, F-ND, P4")

    # F2: 32 exact + 8 boundary -> 8/40 = 0.200 LOSES; recall 1.000 -> P2 FAILED; P1, P4 FAILED
    ld, *_ = _fixture(n_exact=32, n_boundary=8)
    rc, buf, text = run(ld)
    ok(line(buf, "ND1 BLOCK-LOSS").startswith("ND1 BLOCK-LOSS = 0.200 ["), "F2 BLOCK-LOSS 0.200")
    ok(line(buf, "ND1 VERDICT") == "ND1 VERDICT: LOSES", "F2 verdict LOSES")
    ok(line(buf, "F-ND: ").startswith("F-ND: FIRED (ND1 LOSES)"), "F2 F-ND FIRED")
    ok(line(buf, "ND1 FAILS-rule") == "ND1 FAILS-rule: BLOCKS-WELL not read; point 0.200 > 0.10", "F2 FAILS-rule point line")
    ok(line(buf, "PREDICTION P1").endswith("value 0.200 -> FAILED"), "F2 P1 FAILED")
    ok(line(buf, "PREDICTION P2").endswith("value 1.000 -> FAILED"), "F2 P2 recall 1.000 FAILED (> 0.95)")
    ok(line(buf, "PREDICTION P4").endswith("value 0.180 -> FAILED") and "(per seed 0.100/0.200/0.200/0.200/0.200)" in line(buf, "ARMS at tau"), "F2 P4 k-means seed mean 0.180 FAILED (the mean of five seeds, not seed 0)")
    ok("TIER STEM-ONLY: tree misses 0 of 0" in "\n".join(buf) and "TIER SAME-OPTIONS: tree misses 8 of 8" in "\n".join(buf), "F2 tiers: boundary twins SAME-OPTIONS")

    # F3 / F4: 3/40 and 4/40 -> UNDETERMINED (4/40 = 0.10 exactly: not > 0.10)
    for nb, want in ((3, "0.075"), (4, "0.100")):
        ld, *_ = _fixture(n_exact=40 - nb, n_boundary=nb)
        rc, buf, text = run(ld)
        ok(line(buf, "ND1 BLOCK-LOSS").startswith("ND1 BLOCK-LOSS = %s [" % want) and line(buf, "ND1 VERDICT") == "ND1 VERDICT: UNDETERMINED",
           "F %d/40 BLOCK-LOSS %s UNDETERMINED" % (nb, want))
        ok(line(buf, "F-ND: ") == "F-ND: NOT FIRED (ND1 UNDETERMINED)", "F %d/40 F-ND NOT FIRED (UNDETERMINED)" % nb)
        ok(line(buf, "ND1 FAILS-rule").startswith("ND1 FAILS-rule: BLOCKS-WELL not read; upper bound"), "F %d/40 FAILS-rule upper-bound line" % nb)
    ok(line(buf, "PREDICTION P1").endswith("value 0.100 -> FAILED") and line(buf, "PREDICTION P4").endswith("value 0.085 -> HELD"),
       "F4 P1 FAILED (0.100 > 0.08), P4 k-means 0.085 HELD")

    # F5: clustered interval: 9 exact singletons + one EVAL id with 10 misses -> point 10/19; cluster bootstrap lower bound 0
    ld, *_ = _fixture(n_exact=9, big_cluster=10)
    rc, buf, text = run(ld)
    lb = line(buf, "ND1 BLOCK-LOSS")
    ok(lb.startswith("ND1 BLOCK-LOSS = 0.526 [95% 0.000, "), "F5 clustered interval lower bound 0.000 (pairs bootstrap would give ~0.30): %s" % lb[:60])
    ok("cluster sizes 1:9/10:1" in line(buf, "SUPPORT MEASURED") and "Kish m (DEFF at rho=1, upper bound) 5.737" in line(buf, "SUPPORT MEASURED"),
       "F5 cluster sizes and Kish 109/19 = 5.737")

    # F6: comparison fraction P3 FAILED with 3 leaves; unequal leaves: EVAL-weighted vs unweighted differ
    ld, *_ = _fixture(n_leaves=3, per_leaf=20, n_exact=10)
    rc, buf, text = run(ld)
    ok(line(buf, "PREDICTION P3").endswith("value 0.333 -> FAILED") and "scores P3) 0.3333" in line(buf, "COMPARISON FRACTION"), "F6a 3 leaves P3 0.3333 FAILED")
    ld, *_ = _fixture(n_leaves=50, per_leaf=10, n_exact=10, unequal=True)
    rc, buf, text = run(ld)
    ok("registered (mean leaf size / 550, unweighted; scores P3) 0.0200; R4 reading (EVAL-weighted, descriptive) 0.1091" in line(buf, "COMPARISON FRACTION") and line(buf, "PREDICTION P3").endswith("value 0.020 -> HELD"),
       "F6b unequal leaves: P3 scores the registered unweighted 0.0200 (HELD), not the EVAL-weighted 60/550 = 0.109 (C-3)")

    # F3 pinned to the digit (C-4: kills a 90% interval, O1) and C-2's non-degenerate branch
    ld, *_ = _fixture(n_exact=37, n_boundary=3)
    rc, buf, text = run(ld)
    ok(line(buf, "ND1 BLOCK-LOSS").startswith("ND1 BLOCK-LOSS = 0.075 [95% 0.000, 0.175] (TREE-BLOCK misses 3 of 40"), "F3 3/40 bootstrap interval [0.000, 0.175] to the digit (C-4)")
    ok(line(buf, "ND1 CLOPPER-PEARSON").endswith(": 0.204; bootstrap upper 0.175") and "BOOTSTRAP (registered; CP printed beside) = 0.175" in line(buf, "ND1 DECIDING UPPER"),
       "F3 CP upper Beta(0.975; 4, 37) = 0.204 printed, the bootstrap decides (C-2)")
    # F7: 0/30 -> the bootstrap says BLOCKS-WELL, CP 1 - 0.025^(1/30) = 0.116 decides UNDETERMINED; the difference is named
    ld, *_ = _fixture(n_exact=30)
    rc, buf, text = run(ld)
    ok(line(buf, "ND1 VERDICT") == "ND1 VERDICT: UNDETERMINED" and "= 0.116" in line(buf, "ND1 DECIDING UPPER")
       and line(buf, "ND1 bootstrap-only") == "ND1 bootstrap-only verdict BLOCKS-WELL; CP-upper verdict UNDETERMINED; THE TWO DIFFER (named)"
       and line(buf, "ND1 FAILS-rule") == "ND1 FAILS-rule: BLOCKS-WELL not read; upper bound 0.116 > 0.10", "F7 0/30: CP decides UNDETERMINED, difference named (C-2)")
    # F8: 45 exact + 6 multi-leaf twins: R1 0/51 BLOCKS-WELL (CP 0.070); primary-only 6/51 = 0.118 LOSES -> R1-DEPENDENT (C-1)
    ld, *_ = _fixture(n_exact=45, multi=6)
    rc, buf, text = run(ld)
    ok(line(buf, "ND1 VERDICT") == "ND1 VERDICT: BLOCKS-WELL" and line(buf, "SENSITIVITY (R1)").startswith("SENSITIVITY (R1): primary-leaf-only block BLOCK-LOSS 0.118 [95% ")
       and line(buf, "SENSITIVITY (R1)").endswith("-> LOSES; R1-DEPENDENT (differs from the ND1 verdict)"), "F8 primary-only 6/51 = 0.118 LOSES, R1-DEPENDENT named (C-1)")

    # refusals
    ld, *_ = _fixture(n_exact=0, n_near=3)
    r, buf, _ = run(ld)
    ok(isinstance(r, str) and "no stem_key twin pair" in r, "zero positives REFUSED")
    ld, *_ = _fixture(n_exact=0, n_sub=5)
    r, buf, _ = run(ld)
    ok(isinstance(r, str) and "no positive pair is flagged by PLAIN at tau 0.95" in r, "zero PLAIN-flagged positives REFUSED (nothing written)")

    # dry-run: prints denominators, never reads a cosine, writes nothing
    calls = []
    real = globals()["analyze"]
    globals()["analyze"] = lambda *a, **k: calls.append(1) or real(*a, **k)
    try:
        ld, *_ = _fixture(n_exact=40, n_sub=10)
        rc, buf, text = run(ld, ("--dry-run",))
    finally:
        globals()["analyze"] = real
    ok(rc == 0 and text is None and not calls, "dry-run: returns 0, analyze never called, no outcome written")
    ok("DENOMINATORS: EVAL items 50; TRAIN members 1010; leaves 50; pairs 50500; positives 50 pairs / 50 EVAL ids" in "\n".join(buf), "dry-run denominators")
    ok(any(s.startswith("  PIN neardup_audit.py blob:") for s in buf) and any("content_closure.py blob:1533cb5a" in s for s in buf), "dry-run pins")
    ok("Kish m 1.000 vs declared DEFF 1.2" in "\n".join(buf), "dry-run support line (declared vs measured)")

    # write-once: a second --run into the same directory refuses and leaves the file unchanged
    with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT if os.path.isdir(SCRATCH_PARENT) else None) as td:
        ld, *_ = _fixture(n_exact=40)
        main(["--run", "--out-dir", td], loader=ld, out=lambda s: None)
        p = os.path.join(td, OUTCOME)
        before = open(p, "rb").read()
        try:
            main(["--run", "--out-dir", td], loader=ld, out=lambda s: None)
            second = None
        except Refusal as r:
            second = str(r)
        ok(second is not None and "write-once" in second and open(p, "rb").read() == before, "second --run REFUSED, outcome unchanged")
        try:
            write_once(p, "x")
            w2 = None
        except Refusal as r:
            w2 = str(r)
        ok(w2 is not None and open(p, "rb").read() == before, "write_once refuses an existing path")
        sums = open(os.path.join(td, "SHA256SUMS.txt"), encoding="utf-8").read().split()
        ok(sums[0] == hashlib.sha256(before).hexdigest() and sums[1] == OUTCOME, "SHA256SUMS.txt pins the outcome bytes")

    # pin refusal
    try:
        verify_pin("content_closure.py", blob="0" * 40)
        pr = None
    except Refusal as r:
        pr = str(r)
    ok(pr is not None and "registered blob:00000000" in pr, "pin mismatch REFUSED")

    # assemble: EVAL side = the EVAL rows, TRAIN side = the leaves' listed members; counts refused when not registered
    ld, evals, nodes, qtext, vec_of = _fixture(n_leaves=5, per_leaf=4, n_exact=3, multi=True)
    d = ld(None)
    ok(d["eval_ids"] == [e[0] for e in evals] and set(d["member_ids"]) == set(qtext) and len(d["member_ids"]) == 21,
       "assemble: EVAL ids = the EVAL rows; members = 21 listed queryIds (20 + 1 multi-leaf, counted once)")
    mi = d["member_ids"].index("q_" + hashlib.sha256(b"Multi Leaf Twin").hexdigest()[:16])
    ok(d["member_leaves"][mi] == [2, 3] and d["primary"][mi] == 3, "assemble: multi-leaf member listed in leaves [2, 3], primary 3 (weight 0.6)")
    for kw, frag in ((dict(n_leaves=4), "4 leaves" if False else "has 5 leaves, registered 4"), (dict(n_members=20), "21 distinct TRAIN members, registered 20"),
                     (dict(n_eval=3), "4 EVAL rows, registered 3")):
        try:
            assemble(evals, nodes, qtext, vec_of, {}, **dict(dict(n_leaves=5, n_members=21, n_eval=4, dim=64), **kw))
            rr = None
        except Refusal as r:
            rr = str(r)
        ok(rr is not None and frag in rr, "assemble refuses: %s" % frag)
    print("SELFTEST %s: %d failure(s)" % ("PASSED" if not fails else "FAILED", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
