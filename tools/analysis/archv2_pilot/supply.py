"""The per-stratum EVAL SUPPLY JSON that archv2_g22_sim.py --supply-json reads (ruling 2 (v): the real-supply re-run of
the D1 designs and the stop leg), built from the split of record through the sealed eval_view (read-only).

FORMAT (exactly what archv2_g22_sim.supply_from parses: {corpus: {stratum: int}}, nothing else in the file):
  "mmlu"   the MMLU-Pro pool (pv2_6f78aece2bf9a612, corpus_version mmlu-pro-v2 named): anchor -> count, the anchor name
           normalised as the simulator's KeyTable does (stratum_domain strip().lower()), so the keys equal the
           simulator's strata (a mismatch fails loudly in the simulator: strata_pool[corpus][s] KeyError).
  "union"  the mc6 pool (pv2_4cce62591eb5a2cb, corpus_version mc6-2026-09-11 named): "<stratum_source>/<stratum_domain>"
           -> count (KeyTable's union strata are "<source>/<domain>" from corpus_questions; the split's stratum is the
           modal (source, domain) vote of the item's component). D0 and D2 need it; D4 / D1 read "mmlu" only.
COUNT KIND (a REQUIRED argument; the builder does not choose): "items" = the pool's EVAL items (routing-only sentinels
included, the ruling's "EVAL item count"); "judgeable" = EVAL items with at least one ACTIVE-model response in that
corpus (the questions a design can judge). Both are printed; the file carries the one asked for.
--only-anchors <stage-1 record>: the "mmlu" object restricted to the REGISTERED 7 (verified by stage1.verify) and no
"union": with this file design D1-stage1's choose_strata(supply, 7) returns exactly the registered 7 (n >= len(names)
returns all names), so the frozen simulator reads the registered set without any edit. D1-full and the stop leg need
all 14 (see the build report: the stop leg draws its stage-1 set from its own stream and cannot take the 7).
[RE-PINNED 2026-09-24, insertion: the pools are now those of the split of record 5a3e756 (common.POOL_MMLU
pv2_41dbd3dbcd399df0; common.POOL_UNION pv2_1575de61bb20e977, scope "all corpora + mc6-2026-09-11", its mc6 count read from
n_items_by_scope); the ids above are split 1's. U-excluded items are in no view, so no count includes them.]
A sidecar <out>.manifest.json (write-once) records the count kind, the eval_view sha, the pools, the supply file's sha256.
"""
from . import common as C
from . import stage1


def union_strata(conn, cv):
    items = C.eval_items(conn, cv)
    return {iid: "%s/%s" % (src, dom) for iid, (src, dom) in items.items()}


def build(conn, count_kind, record=True, only_anchors=None, out=print):
    if count_kind not in ("items", "judgeable"):
        C.refuse("--count must be 'items' or 'judgeable' (the builder does not choose), got %r" % (count_kind,))
    pm = C.pool_of(conn, C.CV_MMLU, C.POOL_MMLU if record else None)
    pu = C.pool_of(conn, C.CV_UNION, C.POOL_UNION if record else None)
    anchor_of, counts_items, _raw = C.anchor_of_items(conn, C.CV_MMLU, pm)
    jm = C.judgeable_items(conn, C.CV_MMLU)
    counts_judg = {}
    for iid, a in anchor_of.items():
        if iid in jm:
            counts_judg[a] = counts_judg.get(a, 0) + 1
    ustr = union_strata(conn, C.CV_UNION)
    C.need(len(ustr) == pu["n_items"], "the EVAL items of %s (%d) differ from the pool row's n_items %d"
           % (C.CV_UNION, len(ustr), pu["n_items"]))
    ju = C.judgeable_items(conn, C.CV_UNION)
    u_items, u_judg = {}, {}
    for iid, s in ustr.items():
        u_items[s] = u_items.get(s, 0) + 1
        if iid in ju:
            u_judg[s] = u_judg.get(s, 0) + 1
    out("  mmlu (%s, %s): %d anchors, EVAL items %d, judgeable %d" % (pm["pool_id"], C.CV_MMLU, len(counts_items),
                                                                    sum(counts_items.values()), sum(counts_judg.values())))
    for a in sorted(counts_items):
        out("    %-20s items %5d  judgeable %5d" % (a, counts_items[a], counts_judg.get(a, 0)))
    out("  union (%s, %s): %d strata, EVAL items %d, judgeable %d" % (pu["pool_id"], C.CV_UNION, len(u_items),
                                                                    sum(u_items.values()), sum(u_judg.values())))
    for s in sorted(u_items):
        out("    %-50s items %5d  judgeable %5d" % (s, u_items[s], u_judg.get(s, 0)))
    mm = counts_items if count_kind == "items" else {a: counts_judg.get(a, 0) for a in counts_items}
    uu = u_items if count_kind == "items" else {s: u_judg.get(s, 0) for s in u_items}
    supply = {"mmlu": dict(sorted(mm.items())), "union": dict(sorted(uu.items()))}
    if only_anchors is not None:
        seven = stage1.verify(only_anchors, counts=counts_items, record=record)
        supply = {"mmlu": {a: supply["mmlu"][a] for a in seven}}
        out("  RESTRICTED to the registered stage-1 anchors (%s): %s" % (stage1.REGISTRATION, ", ".join(seven)))
    manifest = {"kind": "archv2-supply-json-1", "count_kind": count_kind, "pools": {"mmlu": pm, "union": pu},
                "anchor_counts_digest_items": C.counts_digest(counts_items),
                "restricted_to_stage1": only_anchors is not None,
                "code": C.code_pins(["archv2_pilot/common.py", "archv2_pilot/supply.py", "archv2_pilot/stage1.py"])}
    return supply, manifest
