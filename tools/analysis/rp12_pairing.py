"""rp12_pairing.py: the per-item pairing builders of RP12 ARCH-V2-E-T (B3): the G13 input bundle and the G14 tree-cells file.

REGISTRATION OF RECORD: docs/judge_v2_program.md L22028-L22060 (0a0361b): G13's D13 = P_fl - P(KC_0) "paired on union EVAL";
G14's "per-cell policy fitted on TRAIN with cells read from B0 (flatLeaf-filed (source, domain))". Both need B0's filing PER
ITEM, which the engine's union readout carries only with unionRoutingItemKey = true (RP12 B3): MAIN_union_routing_queries.csv
(held-out rows, trailing item_id), MAIN_union_routing_train_queries.csv (every TRAIN text, same columns) and
MAIN_union_routing_leaves.csv (every leaf's TRAIN-majority domain). ZERO calls; no construction; no statistic is computed here.

READINGS (stated, for the READY to confirm or refuse):
  (P1) ITEM'S CELL = the modal leaf_dominant over the item's routed rows (an item has several rows when twin texts share its
       stem key); ties go to the lexicographically smallest; an unrouted row counts as the cell "<unrouted>". The number of
       items whose rows disagree is printed.
  (P2) G13's per-item flatLeaf filing indicator eval_fl = 1 iff the item's cell (P1) equals its declared class (the rows'
       true_key; rows of one item with different true_key REFUSE). This is the engine's top1 column read at item level.
       [READY_rp12_pair_mc D-3, rp12-flat-pin; insertion only: SUPERSEDED by the MC-EXCLUDE delta (2026-10-01) and its G14
       ruling (b) below: such items are EXCLUDED from G11 D_fd and G13 D13 (1% bar) and disclosed only in G14.]
  (P3) SIDES come from the committed side export (split ARCH-V2-SPLIT-DRAW-2): G13's EVAL = the export's EVAL items tagged
       mc6-2026-09-11 that have a row (the bundle then must hold 6,153 items in 5,642 components or g13_comparator refuses);
       TRAIN = its TRAIN items with a TRAIN row. GATE rows are dropped and counted. A held-out row of a TRAIN item, or a TRAIN
       row of an EVAL item, REFUSES (a split defect).
  (P4) G13's vectors: the item's representative text = the smallest-question_id text of the item among the text sources given
       (corpus_questions of the multi-corpus DB; mmlu_pro when the MMLU-Pro member is on the mmlu_pro table), read from
       embeddings_cache.db (queries of record, qwen3), first --dim components, unit-normalised; a missing vector REFUSES.
  (P5) leaf_major = the leaf table's leaf_dominant of every leaf with profile_size > 0 (leaves with no profile are counted and
       excluded: they have no TRAIN majority).
  (P6) G14's tree cells cover every side-export item tagged mc6-2026-09-11 on TRAIN or EVAL: routed items get P1's cell, the
       rest (items with no corpus text, e.g. response-only items) get "<no-routing-row>" and are counted; v2_declared_cells
       fits that cell's policy on TRAIN like any other cell.

  python tools/analysis/rp12_pairing.py --selftest
  python tools/analysis/rp12_pairing.py --g13-bundle --validation <B0>/validation --texts-db <multicorpus DB> [--texts-mmlu <db>]
         --emb-db embeddings_cache.db --out <stem>          # writes <stem>.npz and <stem>.json (write-once)
  python tools/analysis/rp12_pairing.py --g14-tree-cells --validation <B0>/validation --out <file.tsv>   # prints its sha256 (LF)
  A POOL READER when --texts-db / --emb-db point at DBs of record: never beside a construction.

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; W0 control survived): W1 tie to the
largest cell | W2 first row wins | W3 an unrouted row counted as its declared class | W4 GATE rows kept as EVAL | W5 the
held-out split-defect refusal removed | W6 the item_id-last check removed | W7 fl forced to 1 | W8 the largest question id
represents | W9 leaves without profile kept | W10 the <no-routing-row> fill removed | W11 vectors not normalised | W12 the
bundle not write-once: 12 of 12 killed.
[DELTA 2026-09-30 rp12-et2, READY_rp12_et C-5 / D-3 / D-4; insertion only] <no-routing-row> is counted BY SIDE (the tree-cells
header's no_routing_row_eval / no_routing_row_train, the printed line, a WARNING on any EVAL item; v2_declared_cells refuses
such an item of the scoring set); ties resolved to <unrouted> are counted and printed (D-3); a TRAIN row of a GATE item
refuses, value-tested (D-4, the reviewer's RA4). Mutants: R0 control survived; R1 no-row counted as TRAIN only, R2 unrouted
ties not counted, R3 (RA4) GATE accepted on a TRAIN row: 3 of 3 killed; W1-W12 re-run on the new fixture, 12 of 12 killed.
[DELTA 2026-10-01 rp12-pair-mc, MC-EXCLUDE (orchestrator ruling after B0 step (c) refused on 19 multi-class items of 8,186,
experiment_results/archv2/rp12/B0_run/c_g13_bundle.txt); insertion only; the DEFAULT rule, no flag] P2's "rows of one item with
different true_key REFUSE" is replaced by: such an item is EXCLUDED from every per-item pairing readout (G11 D_fd, G13 D13,
G14). item_cells returns them as a 4th value; multi_by_side files them EVAL / GATE / TRAIN under P3's split-defect rules;
exclusion_lines prints the counts by side, every item key with its classes, and the denominators after the exclusion beside the
counts before it and the registered 6,153 / 5,642; check_exclusion REFUSES iff 100 x excluded EVAL > EVAL items before the
exclusion (more than 1%). The G13 bundle drops them from EVAL and TRAIN and lists them in its json (multiclass_excluded,
n_eval_before_exclusion, n_components_before_exclusion: g13_comparator reads the registered counts BEFORE the exclusion); the
G14 tree-cells file gives them the cell <multi-class> (never <no-routing-row>) and appends multi_class_eval / _gate / _train to
its header only when one is excluded (absent exclusions: the header is unchanged). Selftest case "MC-EXCLUDE" (end to end
through g13_bundle, g13_comparator.load_bundle and g14_tree_cells; 1 of 125 admitted at 0.8000%, 2 of 125 refused at 1.6000%;
the integer bar at 1 of 100 / 2 of 199). Mutants (one temporary edit at a time, reverted; MC0 control survived): MC1 the items
re-included and listed, MC2 re-included under their first class, MC3 the bar at >=, MC4 the bar removed, MC5 GATE filed as
EVAL, MC6 the item keys not printed, MC7 the before-count taken after, MC8 G14 fills them as <no-routing-row>, MC9 the
held-out split defect skipped for them, MC10 the bundle does not list them: 10 of 10 killed.]
[DELTA 2026-10-01 rp12-pair-mc, G14 RULING (b) (orchestrator, after the hand-back of 26908cd); insertion only; supersedes the
G14 sentences of the bracket above] G14 does NOT exclude multi-class items: its declared arm must reproduce RP03's recorded
+2.67pp [+1.46pp, +3.89pp] on the full set, as registered, and the tree cell reads no declared class. g14_tree_cells gives them
P1's modal cell (modal_cells, the same _modal rule as item_cells), writes the pre-rule header, applies no 1% bar, and prints
their keys by side as a DISCLOSURE line only. The exclusion and the 1% bar apply only to G11 D_fd and G13 D13. Mutants (D0
control survived): D1 G14 excludes them again (dropped), D2 G14 gives them <multi-class>, D3 the disclosure keys not printed,
D4 the 1% bar applied in G14: 4 of 4 killed.]
[DELTA 2026-10-01 rp12-flat-pin, READY_rp12_pair_mc D-1 / D-3 (ccef91d); insertion only] D-1: exclusion_lines names only the
readouts that exclude: "every per-item pairing readout that excludes: G11 D_fd, G13 D13 (G14: disclosure only, ruling (b))"
(g11_reader re-pinned; its outcome reuses the line). D-3: the P2 sentence carries a SUPERSEDED bracket. Mutant E1 (the old
wording ", G14):" restored): killed by both selftests.]
[DELTA 2026-10-01 rp12-r2-lane; insertion only] --lane {r1,r2} (tools/analysis/rp12_lane.py; default r1 = the commands of
record, unchanged): --validation and --out of the other lane REFUSE; in lane r2 they must lie inside
experiment_configs/rp12_r2/ or experiment_results/archv2/rp12_r2/.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

import sys
import csv
import json
import struct
import hashlib
import argparse
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import v2_engine_pool as EP  # noqa: E402
from data_v2 import ro  # noqa: E402
from data_v2 import common as C  # noqa: E402

TAG = "[RP12-PAIR]"
UNION_CORPUS = "mc6-2026-09-11"
POOL_UNION = "pv2_1575de61bb20e977"
QUERIES = "MAIN_union_routing_queries.csv"
TRAIN = "MAIN_union_routing_train_queries.csv"
LEAVES = "MAIN_union_routing_leaves.csv"
UNROUTED = "<unrouted>"
NO_ROW = "<no-routing-row>"
MULTI = "<multi-class>"            # MC-EXCLUDE (orchestrator ruling 2026-10-01): an item whose rows carry > 1 declared class
N_EVAL_REG, N_COMP_REG = 6153, 5642   # the registered union EVAL denominators (G11 / G13), printed beside the post-exclusion ones
TREE_CELLS_FORMAT = "taxoarena-tree-cells-v1"


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def sha_lf(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def read_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and "item_id" not in rows[0]:
        refuse("%s carries no item_id column: the B0 readout must run with unionRoutingItemKey = true (RP12 B3)" % path)
    with open(path, encoding="utf-8") as f:
        head = f.readline().strip().split(",")
    if head[-1] != "item_id":
        refuse("%s carries no item_id column: the B0 readout must run with unionRoutingItemKey = true (RP12 B3)" % path)
    return rows


def item_cells(rows):
    """P1 / P2: {item: (cell, true_key, n_rows)}, the count of items whose rows disagree on the cell, (READY_rp12_et D-3)
    the count of ties the rule resolved to <unrouted> (0x3C sorts before every label, so it wins every tie it is in), and
    (MC-EXCLUDE) {item: sorted declared classes} of the items whose rows carry more than one declared class: they are NOT in
    the first map (excluded from every per-item pairing readout; the caller prints them by side and applies the 1% bar)."""
    by = defaultdict(list)
    for r in rows:
        by[r["item_id"]].append(r)
    out, disagree, unrouted_ties, multi = {}, 0, 0, {}
    for it, rs in by.items():
        keys = {r["true_key"] for r in rs}
        if len(keys) != 1:
            multi[it] = sorted(keys)
            continue
        cell, tied, cells = _modal(rs)
        if len(tied) > 1 and cell == UNROUTED:
            unrouted_ties += 1
        if len(cells) > 1:
            disagree += 1
        out[it] = (cell, keys.pop(), len(rs))
    return out, disagree, unrouted_ties, multi


def _modal(rs):
    """P1's rule on one item's rows -> (cell, the tied cells, the Counter); it reads no declared class."""
    cells = Counter((r["leaf_dominant"] if r["leaf_id"] else UNROUTED) or UNROUTED for r in rs)
    top = max(cells.values())
    tied = [c for c, n in cells.items() if n == top]
    return min(tied), tied, cells


def modal_cells(rows, items):
    """G14 RULING (b): P1's cell of each of `items` (the multi-class ones), by the same rule; no declared class is needed."""
    by = defaultdict(list)
    for r in rows:
        if r["item_id"] in items:
            by[r["item_id"]].append(r)
    return {it: _modal(rs)[0] for it, rs in by.items()}


def multi_by_side(multi_held, multi_train, side):
    """MC-EXCLUDE: the excluded items by side {"EVAL": {item: classes}, "GATE": ..., "TRAIN": ...}; the split-defect rules of P3
    apply to them too (a held-out row of a TRAIN item, a TRAIN row of an EVAL / GATE item REFUSE)."""
    ex = {"EVAL": {}, "GATE": {}, "TRAIN": {}}
    for it, ks in multi_held.items():
        s = side.get(it, (None, "ABSENT"))[1]
        if s not in ("EVAL", "GATE"):
            refuse("held-out row of item %s whose side is %s (a split defect)" % (it, s))
        ex[s][it] = ks
    for it, ks in multi_train.items():
        s = side.get(it, (None, "ABSENT"))[1]
        if s != "TRAIN":
            refuse("TRAIN row of item %s whose side is %s (a split defect)" % (it, s))
        ex["TRAIN"][it] = ks
    return ex


def exclusion_lines(ex, n_eval, n_comp, n_eval_before, n_comp_before, tag=TAG):
    """MC-EXCLUDE: the printed block (counts by side, every item key with its classes, the denominators beside the registered
    6,153 / 5,642) and the 1% bar: REFUSED iff more than 1% of the EVAL items (before exclusion) are excluded."""
    k = len(ex["EVAL"])
    o = ["%s MULTI-CLASS ITEMS EXCLUDED (orchestrator ruling 2026-10-01; every per-item pairing readout that excludes: G11 D_fd, G13 D13 (G14: disclosure only, ruling (b))):"
         " EVAL %d, GATE %d, TRAIN %d" % (tag, k, len(ex["GATE"]), len(ex["TRAIN"]))]
    for sd in ("EVAL", "GATE", "TRAIN"):
        for it in sorted(ex[sd]):
            o.append("%s   excluded %s %s %s" % (tag, sd, it, ex[sd][it]))
    o.append("%s DENOMINATORS: EVAL %d items in %d components after the exclusion (before %d / %d; registered %d / %d); EVAL"
             " excluded %d of %d = %.4f%% (bar: refused above 1%%)" % (tag, n_eval, n_comp, n_eval_before, n_comp_before, N_EVAL_REG,
                                                                     N_COMP_REG, k, n_eval_before,
                                                                     100.0 * k / n_eval_before if n_eval_before else 0.0))
    return o


def check_exclusion(n_excl_eval, n_eval_before, tag=TAG):
    """The 1% bar, in integers: REFUSED iff 100 x excluded > EVAL items before the exclusion."""
    if 100 * n_excl_eval > n_eval_before:
        raise SystemExit("%s REFUSED: %d of %d EVAL items (%.4f%%) carry more than one declared class; the exclusion rule admits"
                         " at most 1%%" % (tag, n_excl_eval, n_eval_before, 100.0 * n_excl_eval / n_eval_before))


def sides(side_path, corpus=UNION_CORPUS):
    items, meta = EP.read_side(side_path)
    return {i: (c, s) for i, (c, s, cs) in items.items() if corpus in cs}, meta


def split_items(held, train, side):
    """P3 -> (eval {item: (cell, key)}, train {item: (cell, key)}, counts)."""
    ev, tr, cnt = {}, {}, Counter()
    for it, (cell, key, _n) in held.items():
        s = side.get(it, (None, "ABSENT"))[1]
        if s == "EVAL":
            ev[it] = (cell, key)
        elif s == "GATE":
            cnt["held_gate"] += 1
        else:
            refuse("held-out row of item %s whose side is %s (a split defect)" % (it, s))
    for it, (cell, key, _n) in train.items():
        s = side.get(it, (None, "ABSENT"))[1]
        if s != "TRAIN":
            refuse("TRAIN row of item %s whose side is %s (a split defect)" % (it, s))
        tr[it] = (cell, key)
    return ev, tr, cnt


def leaf_majors(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
    maj = [r["leaf_dominant"] for r in rows if int(r["profile_size"]) > 0 and r["leaf_dominant"]]
    return maj, len(rows) - len(maj)


def item_texts(texts_db, mmlu_db=None):
    """P4: {item: representative text} (smallest id per item) over corpus_questions (+ mmlu_pro when given)."""
    keys = C.KeyCache()
    best = {}
    for path, sql in ((texts_db, "SELECT question_id, text FROM corpus_questions"), (mmlu_db, "SELECT id, question FROM mmlu_pro")):
        if not path:
            continue
        conn = ro.open_ro(path)
        try:
            for qid, t in conn.execute(sql):
                if t is None or EP._kotlin_blank(t):
                    continue
                it = "i:" + keys.stem(t)
                cur = best.get(it)
                if cur is None or (path, qid) < cur[0]:
                    best[it] = ((path, qid), t)
        finally:
            conn.close()
    return {it: t for it, (_k, t) in best.items()}


def vectors(emb_db, texts, dim):
    want = set(texts)
    conn = ro.open_ro(emb_db)
    vec = {}
    try:
        tl = sorted(want)
        for s in range(0, len(tl), 500):
            ch = tl[s:s + 500]
            for t, blob in conn.execute("SELECT query, vector FROM embeddings WHERE query IN (%s)" % ",".join("?" * len(ch)), ch):
                if isinstance(blob, bytes) and len(blob) % 4 == 0 and len(blob) // 4 >= dim:
                    v = np.array(struct.unpack(">%df" % (len(blob) // 4), blob)[:dim], dtype=np.float64)
                    n = np.linalg.norm(v)
                    vec[t] = v / (n if n > 0 else 1.0)
    finally:
        conn.close()
    return vec


def g13_bundle(validation, side_path, texts_db, mmlu_db, emb_db, out_stem, dim=512, out=print):
    for p in (out_stem + ".npz", out_stem + ".json"):
        if os.path.exists(p):
            refuse("%s exists; the bundle is write-once" % p)
    side, smeta = sides(side_path)
    held, d_h, u_h, m_h = item_cells(read_rows(os.path.join(validation, QUERIES)))
    trn, d_t, u_t, m_t = item_cells(read_rows(os.path.join(validation, TRAIN)))
    ev, tr, cnt = split_items(held, trn, side)
    ex = multi_by_side(m_h, m_t, side)
    n_before = len(ev) + len(ex["EVAL"])
    c_before = len({side[i][0] for i in list(ev) + list(ex["EVAL"])})
    for ln in exclusion_lines(ex, len(ev), len({side[i][0] for i in ev}), n_before, c_before):
        out(ln)
    check_exclusion(len(ex["EVAL"]), n_before)
    majors, no_prof = leaf_majors(os.path.join(validation, LEAVES))
    text = item_texts(texts_db, mmlu_db)
    need = sorted(ev) + sorted(tr)
    miss = [i for i in need if i not in text]
    if miss:
        refuse("%d item(s) have no text in the text sources (first %s)" % (len(miss), miss[:3]))
    vec = vectors(emb_db, [text[i] for i in need], dim)
    nov = [i for i in need if text[i] not in vec]
    if nov:
        refuse("%d item(s) have no %d-d vector in %s (first %s)" % (len(nov), dim, emb_db, nov[:3]))
    classes = sorted({k for _c, k in ev.values()} | {k for _c, k in tr.values()} | set(majors))
    ci = {c: j for j, c in enumerate(classes)}
    eids, tids = sorted(ev), sorted(tr)
    comps = [side[i][0] for i in eids]
    _, comp_idx = np.unique(np.array(comps), return_inverse=True)
    arrays = dict(eval_X=np.stack([vec[text[i]] for i in eids]), eval_y=np.array([ci[ev[i][1]] for i in eids]),
                  eval_comp=comp_idx.astype(np.int64), eval_fl=np.array([int(ev[i][0] == ev[i][1]) for i in eids]),
                  train_X=np.stack([vec[text[i]] for i in tids]), train_y=np.array([ci[tr[i][1]] for i in tids]),
                  classes=np.array(classes), leaf_major=np.array(majors), eval_item=np.array(eids), train_item=np.array(tids))
    meta = {"pool_id": POOL_UNION, "dim": dim, "n_eval": len(eids), "n_components": len(set(comps)),
            "n_eval_before_exclusion": n_before, "n_components_before_exclusion": c_before,
            "multiclass_excluded": {sd: ex[sd] for sd in ("EVAL", "GATE", "TRAIN")},
            "readings": "P1-P6 of tools/analysis/rp12_pairing.py",
            "sources": {"queries_sha256_lf": sha_lf(os.path.join(validation, QUERIES)),
                        "train_sha256_lf": sha_lf(os.path.join(validation, TRAIN)),
                        "leaves_sha256_lf": sha_lf(os.path.join(validation, LEAVES)), "side_export": smeta["sha256_lf"],
                        "builder_blob": ro.git_blob_lf(os.path.abspath(__file__)), "emb_db": os.path.basename(emb_db)},
            "counts": {"eval_items": len(eids), "train_items": len(tids), "held_gate_rows_dropped": cnt["held_gate"],
                       "items_rows_disagree_heldout": d_h, "items_rows_disagree_train": d_t, "leaves_no_profile": no_prof,
                       "unrouted_ties_heldout": u_h, "unrouted_ties_train": u_t,
                       "leaves_with_major": len(majors), "classes": len(classes),
                       "multiclass_excluded_eval": len(ex["EVAL"]), "multiclass_excluded_gate": len(ex["GATE"]),
                       "multiclass_excluded_train": len(ex["TRAIN"])}}
    with open(out_stem + ".npz", "xb") as f:
        np.savez(f, **arrays)
    with open(out_stem + ".json", "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    out("%s G13 bundle %s: EVAL %d items in %d components, TRAIN %d, classes %d, leaves with a TRAIN majority %d (%d without"
        " profile); GATE rows dropped %d; items with disagreeing rows: held-out %d, TRAIN %d; ties resolved to %s: held-out %d,"
        " TRAIN %d" % (TAG, out_stem, len(eids), len(set(comps)), len(tids), len(classes), len(majors), no_prof, cnt["held_gate"], d_h,
                       d_t, UNROUTED, u_h, u_t))
    return meta


def g14_tree_cells(validation, side_path, out_path, out=print):
    if os.path.exists(out_path):
        refuse("%s exists; the tree-cells file is write-once" % out_path)
    side, smeta = sides(side_path)
    rows_h, rows_t = read_rows(os.path.join(validation, QUERIES)), read_rows(os.path.join(validation, TRAIN))
    held, d_h, u_h, m_h = item_cells(rows_h)
    trn, d_t, u_t, m_t = item_cells(rows_t)
    ev, tr, cnt = split_items(held, trn, side)
    ex = multi_by_side(m_h, m_t, side)
    # G14 RULING (b) 2026-10-01: G14 does NOT exclude them (its declared arm must reproduce RP03's C1 on the full set and the
    # tree cell reads no declared class): they keep P1's cell; their keys are printed as a DISCLOSURE only; no 1% bar here
    out("%s G14 DISCLOSURE (ruling (b): not excluded from G14; the tree cell needs no declared class): multi-class items EVAL %d,"
        " GATE %d, TRAIN %d" % (TAG, len(ex["EVAL"]), len(ex["GATE"]), len(ex["TRAIN"])))
    for sd in ("EVAL", "GATE", "TRAIN"):
        for it in sorted(ex[sd]):
            out("%s   disclosed %s %s %s" % (TAG, sd, it, ex[sd][it]))
    cells = {i: c for i, (c, _k) in list(ev.items()) + list(tr.items())}
    mc_h, mc_t = modal_cells(rows_h, set(ex["EVAL"])), modal_cells(rows_t, set(ex["TRAIN"]))
    cells.update(mc_h)
    cells.update(mc_t)
    filled = {"EVAL": 0, "TRAIN": 0}                 # READY_rp12_et C-5: counted BY SIDE
    for it, (_c, s) in side.items():
        if s in ("TRAIN", "EVAL") and it not in cells:
            cells[it] = NO_ROW
            filled[s] += 1
    head = "# %s b0_validation=%s rule=flatLeaf side_export=%s readings=P1,P3,P6 no_routing_row_eval=%d no_routing_row_train=%d" % (
        TREE_CELLS_FORMAT, os.path.basename(os.path.normpath(os.path.dirname(os.path.abspath(validation)))) or validation,
        smeta["sha256_lf"][:16], filled["EVAL"], filled["TRAIN"])
    body = head + "\nitem_id\ttree_cell\n" + "".join("%s\t%s\n" % (i, cells[i]) for i in sorted(cells))
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        f.write(body)
    sh = hashlib.sha256(body.encode("utf-8")).hexdigest()
    out("%s G14 tree cells %s: %d items (EVAL %d, TRAIN %d routed; %s: EVAL %d, TRAIN %d), %d distinct cells; items with"
        " disagreeing rows: held-out %d, TRAIN %d; ties resolved to %s: held-out %d, TRAIN %d; GATE rows dropped %d; sha256 (LF) %s"
        " -> pass it as --tree-cells-sha256" % (TAG, out_path, len(cells), len(ev), len(tr), NO_ROW, filled["EVAL"], filled["TRAIN"],
                                                len(set(cells.values())), d_h, d_t, UNROUTED, u_h, u_t, cnt["held_gate"], sh))
    if filled["EVAL"]:
        out("%s WARNING: %d EVAL item(s) have no routing row; v2_declared_cells --tree-cells REFUSES if any of them is in the G14"
            " scoring set (C-5)" % (TAG, filled["EVAL"]))
    return sh


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────

def _fixture(tmp, gate_row_side="GATE", multi=False, bulk=0):
    """Texts DB, embeddings DB (big-endian float32), side export and the three engine CSVs of a tiny union readout.
    multi: three MULTI-CLASS items (twin rows under two declared classes), one per side EVAL / GATE / TRAIN (MC-EXCLUDE);
    bulk: that many extra routed EVAL items (so that one excluded EVAL item can sit under the 1% bar)."""
    ss = C.split_side
    from data_v2 import split as S
    rng = np.random.default_rng(3)
    T = {  # qid -> (text, side, class, routed leaf)
        1000001: ("Bbh a1", "EVAL", "BBH/x", "L1"), 1000002: ("  bbh A1 ", "EVAL", "BBH/x", "L2"),   # twin of 1000001
        1000003: ("Bbh a2", "EVAL", "BBH/x", "L2"), 1000004: ("Bbh a3", "GATE", "BBH/x", "L1"),
        1000005: ("Bbh t1", "TRAIN", "BBH/x", "L1"), 1000006: ("Bbh t2", "TRAIN", "BBH/x", "L1"),
        2000001: ("Math e1", "EVAL", "MATH/y", "L2"), 2000002: ("Math e2", "EVAL", "MATH/y", None),
        2000003: ("Math t1", "TRAIN", "MATH/y", "L2"), 2000004: ("Math t2", "TRAIN", "MATH/y", "L1"),
    }
    if multi:
        T.update({3000001: ("Mc e1", "EVAL", "MATH/y", "L2"), 3000002: ("  mc E1 ", "EVAL", "BBH/x", "L1"),
                  3000003: ("Mc g1", "GATE", "MATH/y", "L2"), 3000004: ("MC g1", "GATE", "BBH/x", "L1"),
                  3000005: ("Mc t1", "TRAIN", "MATH/y", "L2"), 3000006: ("mc t1", "TRAIN", "BBH/x", "L1")})
    for j in range(bulk):
        T[4000000 + j] = ("Bulk e%03d" % j, "EVAL", "BBH/x", "L1")
    dom = {"L1": "BBH/x", "L2": "MATH/y"}
    tdb = os.path.join(tmp, "mc.db"); c = ro.create_new(tdb)
    c.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, text TEXT)")
    for q, v in T.items():
        c.execute("INSERT INTO corpus_questions VALUES (?,?)", (q, v[0]))
    c.commit(); c.close()
    edb = os.path.join(tmp, "emb.db"); c = ro.create_new(edb)
    c.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    for q, v in T.items():
        x = rng.standard_normal(16) if q < 3000000 else np.random.default_rng(q).standard_normal(16)
        c.execute("INSERT INTO embeddings VALUES (?,?)", (v[0], struct.pack(">16f", *x)))
    c.commit(); c.close()
    rows, seen = [], set()
    for q, v in sorted(T.items()):
        k = ss.stem_key(v[0])
        if k in seen:
            continue
        seen.add(k)
        side = v[1] if v[1] != "GATE" else gate_row_side
        rows.append(("i:" + k, "c:" + k, side, v[2].split("/")[0], v[2].split("/")[1], UNION_CORPUS))
    k = ss.stem_key("Response only item")
    rows.append(("i:" + k, "c:" + k, "TRAIN", "BBH", "x", UNION_CORPUS))
    k = ss.stem_key("Response only eval item")               # an EVAL item with no corpus text: no routing row (C-5)
    rows.append(("i:" + k, "c:" + k, "EVAL", "BBH", "x", UNION_CORPUS))
    rows.sort(key=lambda r: r[0])
    side_p = os.path.join(tmp, "side.tsv")
    with open(side_p, "w", encoding="utf-8", newline="\n") as f:
        f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (S.SIDE_EXPORT_FORMAT, S._side_rows_sha(rows), len(rows), "0" * 64))
        f.write("\t".join(S.SIDE_COLS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    val = os.path.join(tmp, "validation"); os.makedirs(val)
    head = "true_key,true_source,rule,leaf_id,leaf_label,leaf_depth,leaf_dominant,leaf_purity,routed_source,routed_domain,top1,source_ok,domain_ok,item_id\n"
    def row(q):
        text, _s, key, leaf = T[q]
        it = "i:" + ss.stem_key(text)
        if leaf is None:
            return "%s,%s,flatLeaf,,,,,,,,0,0,0,%s\n" % (key, key.split("/")[0], it)
        return "%s,%s,flatLeaf,%s,%s,3,%s,0.9000,%s,%s,%d,1,1,%s\n" % (key, key.split("/")[0], leaf, leaf, dom[leaf], dom[leaf].split("/")[0],
                                                                     dom[leaf], int(dom[leaf] == key), it)
    with open(os.path.join(val, QUERIES), "w", encoding="utf-8", newline="\n") as f:
        # the twin's L2 row (1000002) is written FIRST, so "first row wins" and the modal tie rule give different cells
        order = [1000002] + [q for q in T if q != 1000002]
        f.write(head + "".join(row(q) for q in order if T[q][1] in ("EVAL", "GATE")))
    with open(os.path.join(val, TRAIN), "w", encoding="utf-8", newline="\n") as f:
        f.write(head + "".join(row(q) for q in T if T[q][1] == "TRAIN"))
    with open(os.path.join(val, LEAVES), "w", encoding="utf-8", newline="\n") as f:
        f.write("leaf_id,leaf_label,leaf_depth,profile_size,leaf_dominant,leaf_purity\nL1,L1,3,3,BBH/x,0.6667\nL2,L2,3,2,MATH/y,1.0000\nL3,L3,3,0,,\n")
    return val, side_p, tdb, edb


def selftest():
    import io, tempfile, shutil, contextlib
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="rp12pair_")
        try:
            fn(tmp)
            print("  ok   " + name)
        except (AssertionError, SystemExit, Exception) as e:
            fails.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))
        finally:
            for d, _ds, fs in os.walk(tmp):
                for f in fs:
                    os.chmod(os.path.join(d, f), 0o666)
            shutil.rmtree(tmp, ignore_errors=True)

    ss = C.split_side
    it = lambda t: "i:" + ss.stem_key(t)

    def bundle(tmp):
        val, side, tdb, edb = _fixture(tmp)
        stem = os.path.join(tmp, "b")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            meta = g13_bundle(val, side, tdb, None, edb, stem, dim=8)
        z = np.load(stem + ".npz", allow_pickle=False)
        eids = list(z["eval_item"])
        assert sorted(eids) == sorted([it("Bbh a1"), it("Bbh a2"), it("Math e1"), it("Math e2")]), eids
        fl = dict(zip(eids, z["eval_fl"].tolist()))
        # the twin item a1 has rows L1 (BBH/x) and L2 (MATH/y): tie -> smallest cell "BBH/x" == its class -> 1 (P1 / P2)
        assert fl[it("Bbh a1")] == 1 and fl[it("Bbh a2")] == 0 and fl[it("Math e1")] == 1 and fl[it("Math e2")] == 0, fl
        assert list(z["classes"]) == ["BBH/x", "MATH/y"] and sorted(z["leaf_major"].tolist()) == ["BBH/x", "MATH/y"]
        assert sorted(z["train_item"].tolist()) == sorted([it("Bbh t1"), it("Bbh t2"), it("Math t1"), it("Math t2")])
        assert z["eval_X"].shape == (4, 8) and abs(np.linalg.norm(z["eval_X"][0]) - 1.0) < 1e-12
        # the representative text of the twin item is the smaller question_id's ("Bbh a1", not "  bbh A1 ")
        vec_a1 = z["eval_X"][eids.index(it("Bbh a1"))]
        conn = ro.open_ro(edb)
        blob = conn.execute("SELECT vector FROM embeddings WHERE query = 'Bbh a1'").fetchone()[0]
        conn.close()
        v = np.array(struct.unpack(">16f", blob)[:8]); v = v / np.linalg.norm(v)
        assert np.allclose(vec_a1, v), (vec_a1, v)
        c = meta["counts"]
        assert (c["held_gate_rows_dropped"], c["items_rows_disagree_heldout"], c["leaves_no_profile"]) == (1, 1, 1), c
        assert len(set(z["eval_comp"].tolist())) == 4
        # the bundle loads and runs through g13_comparator (the contract), on the fixture's own expectation
        import sqlite3
        before = sqlite3.connect
        import g13_comparator as G13       # imports flat_mix_mmlu, whose read-only connect guard is process-wide
        sqlite3.connect = getattr(sqlite3.connect, "_raw", before)   # restored: this selftest writes temp fixtures
        b, m = G13.load_bundle(stem, expect=(POOL_UNION, 4, 4))
        r = G13.compute(b)
        assert abs(r["p_fl"] - 0.5) < 1e-12 and r["n"] == 4 and r["kc"] == {"BBH/x": 1, "MATH/y": 1}, r
        # write-once
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                g13_bundle(val, side, tdb, None, edb, stem, dim=8)
            raise AssertionError("second write not refused")
        except SystemExit as e:
            assert str(e).endswith("exists; the bundle is write-once"), e

    def cells(tmp):
        val, side, tdb, edb = _fixture(tmp)
        p = os.path.join(tmp, "cells.tsv")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sh = g14_tree_cells(val, side, p)
        lines = open(p, encoding="utf-8").read().split("\n")
        assert lines[0].startswith("# taxoarena-tree-cells-v1 ") and lines[0].endswith("no_routing_row_eval=1 no_routing_row_train=1") \
            and lines[1] == "item_id\ttree_cell", lines[0]
        assert "(EVAL 4, TRAIN 4 routed; <no-routing-row>: EVAL 1, TRAIN 1)" in buf.getvalue(), buf.getvalue()
        assert buf.getvalue().splitlines()[-1].startswith("%s WARNING: 1 EVAL item(s) have no routing row" % TAG), buf.getvalue()
        got = dict(l.split("\t") for l in lines[2:] if l)
        assert got[it("Bbh a1")] == "BBH/x" and got[it("Bbh a2")] == "MATH/y" and got[it("Math e2")] == UNROUTED
        assert got[it("Math t2")] == "BBH/x" and got[it("Response only item")] == NO_ROW and it("Bbh a3") not in got, got
        assert got[it("Response only eval item")] == NO_ROW and len(got) == 10
        import v2_declared_cells as V
        cm, desc = V.load_tree_cells(p, sh)
        assert cm == got and "10 items, 4 distinct tree cells" in desc, desc

    def refusals(tmp):
        val, side, tdb, edb = _fixture(tmp, gate_row_side="TRAIN")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                g14_tree_cells(val, side, os.path.join(tmp, "c.tsv"))
            raise AssertionError("a held-out row of a TRAIN item not refused")
        except SystemExit as e:
            assert "held-out row of item" in str(e) and "whose side is TRAIN (a split defect)" in str(e), e
        q = os.path.join(val, QUERIES)
        data = open(q, encoding="utf-8").read().replace(",item_id\n", "\n", 1)
        data = "\n".join(",".join(l.split(",")[:-1]) if i else l for i, l in enumerate(data.split("\n")) if l) + "\n"
        with open(q, "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
        try:
            read_rows(q)
            raise AssertionError("an un-keyed readout not refused")
        except SystemExit as e:
            assert "carries no item_id column" in str(e), e
        rows = [{"item_id": "i:x", "true_key": "A", "leaf_id": "L", "leaf_dominant": "A"},
                {"item_id": "i:x", "true_key": "B", "leaf_id": "L", "leaf_dominant": "A"}]
        # MC-EXCLUDE: two classes are EXCLUDED (no longer refused): absent from the cell map, listed with both classes
        cmx, _dx, _ux, mcx = item_cells(rows + [{"item_id": "i:w", "true_key": "A", "leaf_id": "L", "leaf_dominant": "A"}])
        assert "i:x" not in cmx and mcx == {"i:x": ["A", "B"]} and cmx == {"i:w": ("A", "A", 1)}, (cmx, mcx)
        # modal rule: two rows A, one row B -> A; a tie -> the smaller name
        cm, dis, ut, _m = item_cells([{"item_id": "i:y", "true_key": "K", "leaf_id": "1", "leaf_dominant": d} for d in ("B", "A", "B")])
        assert cm["i:y"] == ("B", "K", 3) and dis == 1 and ut == 0
        # D-3: a tie with an unrouted row resolves to <unrouted> and is counted
        cmu, _d, ut2, _m2 = item_cells([{"item_id": "i:u", "true_key": "K", "leaf_id": "", "leaf_dominant": ""},
                                    {"item_id": "i:u", "true_key": "K", "leaf_id": "1", "leaf_dominant": "A"}])
        assert cmu["i:u"][0] == UNROUTED and ut2 == 1
        # D-4 (READY RA4): a TRAIN routing row of a GATE item refuses, as one of an EVAL item does
        sd = {"i:g": ("c:g", "GATE"), "i:e": ("c:e", "EVAL"), "i:t": ("c:t", "TRAIN")}
        for bad_item, word in (("i:g", "GATE"), ("i:e", "EVAL")):
            try:
                split_items({}, {bad_item: ("K", "K", 1)}, sd)
                raise AssertionError("a TRAIN row of a %s item not refused" % word)
            except SystemExit as e:
                assert str(e) == "%s REFUSED: TRAIN row of item %s whose side is %s (a split defect)" % (TAG, bad_item, word), e
        assert split_items({}, {"i:t": ("K", "K", 1)}, sd)[1] == {"i:t": ("K", "K")}
        cm2, _, _u, _m3 = item_cells([{"item_id": "i:z", "true_key": "K", "leaf_id": "1", "leaf_dominant": d} for d in ("B", "A")])
        assert cm2["i:z"][0] == "A", cm2
        # item_id must be the LAST column (the engine appends it); a readout with a column after it is refused
        q2 = os.path.join(tmp, "q2.csv")
        with open(q2, "w", encoding="utf-8", newline="\n") as f:
            f.write("true_key,item_id,extra\nA,i:x,1\n")
        try:
            read_rows(q2)
            raise AssertionError("item_id not last, not refused")
        except SystemExit as e:
            assert "carries no item_id column" in str(e), e

    def lane_paths(tmp):
        r1v, r2v = "experiment_results/archv2/rp12/B0/graft_flatleaf/seed_42/validation", "experiment_results/archv2/rp12_r2/B0/graft_flatleaf/seed_42/validation"
        for argv, needle in ((["--g14-tree-cells", "--lane", "r2", "--validation", r1v, "--out", "experiment_results/archv2/rp12_r2/g14/cells.tsv"],
                              "--validation %s is an object of lane r1, the run is lane r2" % r1v),
                             (["--g14-tree-cells", "--validation", r2v, "--out", os.path.join(tmp, "c.tsv")], "is an object of lane r2, the run is lane r1"),
                             (["--g14-tree-cells", "--lane", "r2", "--validation", r2v, "--out", os.path.join(tmp, "c.tsv")], "is outside lane r2's roots")):
            try:
                main(argv)
                raise AssertionError("not refused: %s" % argv)
            except SystemExit as e:
                assert needle in str(e), (needle, str(e))

    def mc_exclude(tmp):
        """MC-EXCLUDE end to end through g13_bundle and g14_tree_cells: 1 EVAL, 1 GATE, 1 TRAIN multi-class item excluded,
        printed by side with the keys, the denominators beside 6,153 / 5,642; the 1% bar refuses 2 of 125."""
        val, side, tdb, edb = _fixture(tmp, multi=True, bulk=120)
        stem = os.path.join(tmp, "b")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            meta = g13_bundle(val, side, tdb, None, edb, stem, dim=8)
        t = buf.getvalue()
        e1, g1, t1 = it("Mc e1"), it("Mc g1"), it("Mc t1")
        assert "%s MULTI-CLASS ITEMS EXCLUDED (orchestrator ruling 2026-10-01; every per-item pairing readout that excludes: G11" \
               " D_fd, G13 D13 (G14: disclosure only, ruling (b))): EVAL 1, GATE 1, TRAIN 1" % TAG in t and ", G14):" not in t, t
        for sd, i in (("EVAL", e1), ("GATE", g1), ("TRAIN", t1)):
            assert "%s   excluded %s %s ['BBH/x', 'MATH/y']" % (TAG, sd, i) in t, (sd, t)
        # 4 + 120 kept EVAL items in 124 components; before: 125 / 125; 1 of 125 = 0.8000%
        assert "%s DENOMINATORS: EVAL 124 items in 124 components after the exclusion (before 125 / 125; registered 6153 / 5642);" \
               " EVAL excluded 1 of 125 = 0.8000%% (bar: refused above 1%%)" % TAG in t, t
        z = np.load(stem + ".npz", allow_pickle=False)
        ev_items, tr_items = set(z["eval_item"].tolist()), set(z["train_item"].tolist())
        assert e1 not in ev_items and t1 not in tr_items and g1 not in ev_items and len(ev_items) == 124 and len(tr_items) == 4
        assert (meta["n_eval"], meta["n_eval_before_exclusion"], meta["n_components_before_exclusion"]) == (124, 125, 125), meta
        assert meta["multiclass_excluded"] == {"EVAL": {e1: ["BBH/x", "MATH/y"]}, "GATE": {g1: ["BBH/x", "MATH/y"]},
                                               "TRAIN": {t1: ["BBH/x", "MATH/y"]}}, meta["multiclass_excluded"]
        c = meta["counts"]
        assert (c["multiclass_excluded_eval"], c["multiclass_excluded_gate"], c["multiclass_excluded_train"]) == (1, 1, 1), c
        # the contract: g13_comparator admits the bundle against the PRE-exclusion counts (125 / 125), never the post ones
        import sqlite3
        before = sqlite3.connect
        import g13_comparator as G13
        sqlite3.connect = getattr(sqlite3.connect, "_raw", before)
        b13, m13 = G13.load_bundle(stem, expect=(POOL_UNION, 125, 125))
        assert len(b13["eval_y"]) == 124 and "%s DENOMINATORS: EVAL 124 items in 124 components after the exclusion (before 125 / 125;"             " registered 6153 / 5642)" % G13.TAG in G13.exclusion_lines(m13, 124, 124), G13.exclusion_lines(m13, 124, 124)
        try:
            G13.load_bundle(stem, expect=(POOL_UNION, 124, 124))
            raise AssertionError("post-exclusion counts admitted as the registered ones")
        except SystemExit as e:
            assert "before the multi-class exclusion, not the registered 124 / 124" in str(e), e
        # G14 RULING (b): NOT excluded: the multi-class TRAIN / EVAL items keep P1's modal cell (a tie of their two rows L1 BBH/x
        # and L2 MATH/y -> the smaller, BBH/x), the header is the pre-rule one, the keys are printed as a disclosure only
        p = os.path.join(tmp, "cells.tsv")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            g14_tree_cells(val, side, p)
        lines = open(p, encoding="utf-8").read().split("\n")
        assert lines[0].endswith("no_routing_row_eval=1 no_routing_row_train=1"), lines[0]
        got = dict(l.split("\t") for l in lines[2:] if l)
        assert got[e1] == "BBH/x" and got[t1] == "BBH/x" and g1 not in got and MULTI not in got.values(), (got.get(e1), got.get(t1))
        tg = buf.getvalue()
        assert "%s G14 DISCLOSURE (ruling (b): not excluded from G14; the tree cell needs no declared class): multi-class items" \
               " EVAL 1, GATE 1, TRAIN 1" % TAG in tg, tg
        for sd, i in (("EVAL", e1), ("GATE", g1), ("TRAIN", t1)):
            assert "%s   disclosed %s %s ['BBH/x', 'MATH/y']" % (TAG, sd, i) in tg, (sd, tg)
        assert "EXCLUDED" not in tg and "DENOMINATORS" not in tg, tg
        # the 1% bar through the real entry points: 2 excluded EVAL items of 125 (1.6000%) REFUSE, before anything is written
        os.makedirs(os.path.join(tmp, "x"))
        val2, side2, tdb2, edb2 = _fixture(os.path.join(tmp, "x"), multi=True, bulk=120)
        q = os.path.join(val2, QUERIES)
        k2 = "i:" + ss.stem_key("Bulk e000")
        data = open(q, encoding="utf-8").read().split("\n")
        extra = [l for l in data if l.endswith("," + k2)][0].replace("BBH/x,BBH,", "MATH/y,MATH,", 1)
        with open(q, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(data[:-1] + [extra, ""]))
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                g13_bundle(val2, side2, tdb2, None, edb2, os.path.join(tmp, "x", "b"), dim=8)
            raise AssertionError("2 of 125 not refused by g13_bundle")
        except SystemExit as e:
            assert str(e) == ("%s REFUSED: 2 of 125 EVAL items (1.6000%%) carry more than one declared class; the exclusion rule"
                              " admits at most 1%%" % TAG), e
        assert not os.path.exists(os.path.join(tmp, "x", "b.npz"))
        # G14 RULING (b): no 1% bar in G14: the same 2 of 125 are disclosed and the file is written, every item with its cell
        with contextlib.redirect_stdout(io.StringIO()) as b2:
            g14_tree_cells(val2, side2, os.path.join(tmp, "x", "c.tsv"))
        got2 = dict(l.split("\t") for l in open(os.path.join(tmp, "x", "c.tsv"), encoding="utf-8").read().split("\n")[2:] if l)
        assert got2[k2] == "BBH/x" and got2[e1] == "BBH/x" and "multi-class items EVAL 2, GATE 1, TRAIN 1" in b2.getvalue(), b2.getvalue()
        # the bar in integers: exactly 1% passes, one more refuses; zero EVAL items pass
        check_exclusion(1, 100); check_exclusion(2, 200); check_exclusion(0, 0)
        for k, n in ((2, 199), (1, 99)):
            try:
                check_exclusion(k, n)
                raise AssertionError("%d of %d not refused" % (k, n))
            except SystemExit as e:
                assert "%d of %d EVAL items" % (k, n) in str(e), e
        # a multi-class item keeps the split-defect rules (a held-out row of a TRAIN item refuses)
        try:
            multi_by_side({"i:q": ["A", "B"]}, {}, {"i:q": ("c:q", "TRAIN")})
            raise AssertionError("held-out multi-class row of a TRAIN item not refused")
        except SystemExit as e:
            assert "held-out row of item i:q whose side is TRAIN (a split defect)" in str(e), e
        try:
            multi_by_side({}, {"i:q": ["A", "B"]}, {"i:q": ("c:q", "EVAL")})
            raise AssertionError("TRAIN multi-class row of an EVAL item not refused")
        except SystemExit as e:
            assert "TRAIN row of item i:q whose side is EVAL (a split defect)" in str(e), e

    for nm, fn in [("G13 bundle: items, P1 tie rule, fl, vectors, counts, runs through g13_comparator, write-once", bundle),
                   ("G14 tree cells: P1 cells, <unrouted>, <no-routing-row>, GATE dropped, loads in v2_declared_cells", cells),
                   ("refusals: split defect, un-keyed readout, two classes; the modal rule", refusals),
                   ("MC-EXCLUDE: G11 / G13 excluded by side with keys, denominators, the 1% bar; G14 disclosure only (ruling (b))", mc_exclude),
                   ("rp12-r2-lane: lane guards on --validation / --out", lane_paths)]:
        case(nm, fn)
    print("%s selftest: %d / %d passed" % (TAG, len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--g13-bundle", action="store_true")
    g.add_argument("--g14-tree-cells", action="store_true")
    ap.add_argument("--validation"); ap.add_argument("--side", default=os.path.join(ROOT, EP.DEFAULT_SIDE))
    ap.add_argument("--texts-db"); ap.add_argument("--texts-mmlu"); ap.add_argument("--emb-db"); ap.add_argument("--dim", type=int, default=512)
    ap.add_argument("--out")
    import rp12_lane as LN
    LN.add_arg(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.validation and a.out):
        refuse("--validation and --out are required")
    LN.guard(a.lane, [("--validation", a.validation), ("--out", a.out)])                           # rp12-r2-lane
    if a.g13_bundle:
        if not (a.texts_db and a.emb_db):
            refuse("--g13-bundle needs --texts-db and --emb-db")
        g13_bundle(a.validation, a.side, a.texts_db, a.texts_mmlu, a.emb_db, a.out, dim=a.dim)
    else:
        g14_tree_cells(a.validation, a.side, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
