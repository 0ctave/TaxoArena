"""data_v2.split (M2): a FRESH, SEEDED, RANDOM split under CK-CLOSE-v1, computed ONCE into a sealed `side` DB.

THE AUTHOR'S DECISION (relayed by the orchestrator, 2026-09-23): a fresh, seeded, random split, stratified by (source,
domain), drawn over union-find COMPONENTS so twins never straddle the sides, under CK-CLOSE-v1 with its four conditions,
EVAL ratio 0.30, new pool ids, and a seed that is a PARAMETER. The registrar registers the seed before the real draw; until
then only a DEV seed ("DEV-...") runs, and every output is labelled "DEV, NOT OF RECORD". A non-DEV seed is refused unless
--registration names the record entry that registered it. [CORRECTED 2026-09-24 on READY_archv2_ED D1: that was a
presence check; check_draw now admits a non-DEV seed ONLY as the exact (registration, seed) pair pinned in
REGISTERED_DRAWS, and refuses a DEV seed that carries a registration.]
THE DRAW'S EVIDENCE (READY_archv2_ED D3): export_side writes the sealed `side` table as LF text, one row per item, with its
table_sha in the header; verify_side_export recomputes that sha from the text and compares it with the sealed DB's.
[CK-CLOSE-v2, 2026-09-24 (ARCH-V2-CK-CLOSE-V2, registered at 7cf6284, docs/judge_v2_program.md L16101-L16130): RULE is now
"CK-CLOSE-v2" = CK-CLOSE-v1 (the four conditions below, unchanged) + apply_closure_v2, run inside load_corpora BEFORE any
stratum or draw: (U) the universe keeps an item iff it has a corpus source_row or an ACTIVE-model response (author choice 1:
the quarantined-only items leave the split; they are listed in the split's excluded_u table and are in no view); (P / O / D)
passage_closure.py (its own pin in data_v2/common.py) computes the passage, option and degree-normaliser edges over the
universe, and each edge joins the union-find as a family "P:a|b" / "O:a|b" / "D:a|b", so the family-crossing check of
condition 3 covers it. The edges are stored in the split's closure_edge table. The registered draw is ARCH-V2-SPLIT-DRAW-2;
draw 1 is RETIRED (refused by check_draw). The stratum / rank / rounding / pool-id rules below are unchanged.]

UNITS AND COMPONENTS
  item        "i:"+stem_key, GLOBAL across the corpora of the build (condition 2: the same stem in two corpora is ONE
              item, so it cannot sit on two sides)
  component   union-find over items, joined by
                (a) the stem itself (GPQA's nested subset copies and every cross-source twin collapse here);
                (b) item.family_id where a corpus declares one (BFCL index family, Multi-SWE repo; condition 3; none in
                    MMLU-Pro or the union corpus);
                (c) the LEGACY QUESTION ID FAMILY within one corpus: every item an ACTIVE model was shown under one upstream
                    question id, plus that id's own corpus row where the response table's id IS the corpus row's primary
                    key (the union corpus). This only MERGES (a conservative closure edge, never a content join): 10
                    MMLU-Pro qids whose active rows carry two stems would otherwise put two renderings of one upstream
                    question on two sides. QUARANTINED models contribute NO edge (their ids are shifted: 7,424 of 7,510).
              component_id = "c:" + the smallest stem_key in it.
  stratum     (source, domain) by the MODAL vote of the component's upstream corpus rows (source_row.source,
              source_row.domain); an item with no corpus row votes with its ACTIVE responses (source, eval category), and
              with its quarantined ones only when it has nothing else. Ties go to the lexicographically smallest
              (source, domain). Components whose votes span strata are counted and printed (multi_stratum).

THE DRAW (per stratum; deterministic in the seed):
  rank(component) = sha256("taxoarena-split-v2" US seed US component_id) as hex; components sorted by rank;
  n_eval = floor(0.30 * n + 0.5), n_gate = floor(0.10 * n + 0.5) (capped at n - n_eval); the first n_eval are EVAL, the
  next n_gate GATE, the rest TRAIN. GATE at 0.10 of the whole keeps split_side's 30 / 10 / 60 shares (EVAL_UPPER 300,
  GATE 300-400 of 1000).

CK-CLOSE-v1, THE FOUR CONDITIONS, CHECKED ON THE RESULT (content_closure.py, reused):
  (1) sentinels   every EVAL unit is in the key set: judgeable EVAL units (an ACTIVE response exists) are passed as
                  reserved, the routing-only rest EXPLICITLY as sentinels (assert_content_disjoint's required argument)
  (2) global      one build_closure over all corpora (parts per corpus version); it must move 0 units
  (3) family      qid families and declared families crossing sides: must be 0
  (4) cluster     no EVAL unit is dropped (every unit of an EVAL item is EVAL); reserved_clusters gives the cluster ids
                  and the Kish bound (sum n^2 / n = DEFF at rho = 1, an UPPER bound, never a measured DEFF)
  A failed check REFUSES (raise SystemExit), never an assert.

POOL IDS: "pv2dev_" (DEV) or "pv2_" + sha256(sorted EVAL component ids, LF-joined)[:16], for the whole build and for each
corpus (the EVAL components with a member in that corpus). They are NEW ids and never collide with pool_guard's "p"+16 hex.
"""
import hashlib
import json
import os
from collections import Counter, defaultdict

from . import common as C
from . import ro

EVAL, GATE, TRAIN = "EVAL", "GATE", "TRAIN"
RULE = "CK-CLOSE-v2"
DRAW_TAG = "taxoarena-split-v2"
DEFAULT_EVAL_RATIO = 0.30
DEFAULT_GATE_RATIO = 0.10
# The ONLY non-DEV draws this code runs: registration entry -> seed string, as registered BEFORE any code touched them
# (docs/judge_v2_program.md, "THE SEED OF THE REAL DRAW, REGISTERED BEFORE ANY CODE TOUCHES IT", L15145). A new draw is a
# new registration AND a new line here (reviewed); check_draw compares both values.
REGISTERED_DRAWS = {
    # CK-CLOSE-v2's draw, registered at 7cf6284 (docs/judge_v2_program.md L16128) before any code touched it
    "ARCH-V2-SPLIT-DRAW-2": "ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2"}
# Draws already run, REFUSED for ever (each runs exactly once; "ARCHV2-SPLIT-1 is NEVER reused", L16128): draw 1 ran under
# CK-CLOSE-v1 at b51eb71 (superseded for forward use by the author's redraw decision, 2929bd4). Under this code (v2) it
# would produce a DIFFERENT split under the same name, so it is refused here, by entry and by seed.
RETIRED_DRAWS = {"ARCH-V2-SPLIT-DRAW-1": "ARCHV2-SPLIT-1:c03031568a0a9d827d834b075512b8e4dd095642"}

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE component (component_id TEXT PRIMARY KEY, n_items INTEGER NOT NULL, stratum_source TEXT NOT NULL,
    stratum_domain TEXT NOT NULL, n_strata_voted INTEGER NOT NULL, rank_hex TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('EVAL','GATE','TRAIN'))) WITHOUT ROWID;
CREATE TABLE side (item_id TEXT PRIMARY KEY, component_id TEXT NOT NULL REFERENCES component(component_id),
    side TEXT NOT NULL CHECK (side IN ('EVAL','GATE','TRAIN')), stratum_source TEXT NOT NULL, stratum_domain TEXT NOT NULL,
    corpora TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE stratum (stratum_source TEXT NOT NULL, stratum_domain TEXT NOT NULL, n_components INTEGER NOT NULL,
    n_items INTEGER NOT NULL, n_eval INTEGER NOT NULL, n_gate INTEGER NOT NULL, n_train INTEGER NOT NULL,
    n_eval_items INTEGER NOT NULL, PRIMARY KEY (stratum_source, stratum_domain)) WITHOUT ROWID;
CREATE TABLE pool (pool_id TEXT PRIMARY KEY, scope TEXT NOT NULL, n_components INTEGER NOT NULL,
    n_items_by_scope TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE excluded_u (item_id TEXT PRIMARY KEY) WITHOUT ROWID;
CREATE TABLE closure_edge (kind TEXT NOT NULL CHECK (kind IN ('P','O','D')), item_a TEXT NOT NULL, item_b TEXT NOT NULL,
    CHECK (item_a < item_b), PRIMARY KEY (kind, item_a, item_b)) WITHOUT ROWID;
CREATE INDEX idx_side_component ON side(component_id);
"""
# The registration's DEV-SIM expectations (L16118-L16119; NOT OF RECORD, measured BEFORE U), printed beside ours (K5).
DEV_SIM = {"components_before_u": 18938, "largest_before_u": 14, "largest_mmlu_pro_before_u": 6,
           "history_components_before_u": 293, "multi_stratum_before_u": 68,
           "kish_eval": {"MMLU_PRO": 1.185, "BBH": 1.80, "MUSR": 2.44}, "eval_share_band": (0.2984, 0.3027)}


def _refuse(msg):
    raise SystemExit("[SPLIT-V2] " + msg)


class _UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            if rb < ra:
                ra, rb = rb, ra
            self.p[rb] = ra


def load_corpora(corpus_paths, out=print):
    """Read every sealed corpus_v2 DB (read-only, seal required). Returns a dict with the units the split needs."""
    data = {"corpora": [], "items": {}, "families": [], "votes": defaultdict(Counter), "resp_votes": defaultdict(Counter),
            "q_votes": defaultdict(Counter), "units": {}, "item_corpora": defaultdict(set), "stems": defaultdict(set),
            "options": defaultdict(set)}
    for path in corpus_paths:
        sha = ro.file_sha256(path)
        conn = ro.open_ro(path, require_sealed=True)
        try:
            meta = dict(conn.execute("SELECT key, value FROM meta"))
            cv = meta["corpus_version"]
            C.guard_retired(conn, path)
            if meta.get("content_closure_blob") != C.PINS["content_closure"] or meta.get("split_side_blob") != C.PINS["split_side"]:
                _refuse("%s was built with other instrument pins (%s / %s)" % (path, meta.get("content_closure_blob"),
                                                                              meta.get("split_side_blob")))
            # the BASENAME only: no absolute path enters a DB, so the split's bytes (and the gen_view salt derived from
            # them) do not depend on where the build ran (READY_archv2_ED D9)
            data["corpora"].append({"corpus_version": cv, "path": os.path.basename(path), "sha256_bytes": sha})
            quarantined = {m for (m,) in conn.execute("SELECT model FROM model_registry WHERE status='QUARANTINED'")}
            for iid, sk, fam in conn.execute("SELECT item_id, stem_key, family_id FROM item ORDER BY item_id"):
                data["items"][iid] = sk
                data["item_corpora"][iid].add(cv)
                if fam:
                    data["families"].append(("fam:%s" % fam, iid))
            for rid, iid, src, dom in conn.execute("SELECT source_row_id, item_id, source, domain FROM source_row"
                                                   " ORDER BY source_row_id"):
                data["votes"][iid][(src, dom if dom is not None else "")] += 1
            # judgeable variants: seen by at least one ACTIVE model
            judged = {v for (v,) in conn.execute(
                "SELECT DISTINCT r.seen_ck FROM response r JOIN model_registry m ON m.model = r.model WHERE m.status='ACTIVE'")}
            for rid, iid, vid, text in conn.execute("SELECT source_row_id, item_id, variant_id, text FROM source_row"
                                                    " ORDER BY source_row_id"):
                data["units"][rid] = {"corpus": cv, "item": iid, "text": text, "judgeable": vid in judged, "kind": "source_row"}
            for vid, iid, stem in conn.execute("SELECT variant_id, item_id, stem FROM variant WHERE origin='response'"
                                               " ORDER BY variant_id"):
                data["units"]["%s|%s" % (cv, vid)] = {"corpus": cv, "item": iid, "text": stem, "judgeable": vid in judged,
                                                      "kind": "response_variant"}
            qid_row_item = {}
            if cv == "mc6-2026-09-11":
                # the union's response id IS the corpus row's primary key (corpus_questions.question_id)
                for pk, iid in conn.execute("SELECT upstream_pk, item_id FROM source_row WHERE corpus_table='corpus_questions'"):
                    qid_row_item[pk] = iid
            fam_items = defaultdict(set)
            for qid, model, iid, src, cat in conn.execute("SELECT legacy_qid, model, item_id, source, category FROM response"
                                                          " ORDER BY legacy_qid, model"):
                if model in quarantined:
                    data["q_votes"][iid][(src, cat)] += 1
                    continue
                data["resp_votes"][iid][(src, cat)] += 1
                fam_items[qid].add(iid)
            for qid, its in fam_items.items():
                if qid in qid_row_item:
                    its = its | {qid_row_item[qid]}
                for iid in its:
                    data["families"].append(("qid:%s:%s" % (cv, qid), iid))
            for iid, stem, oj in conn.execute("SELECT item_id, stem, options_sorted_json FROM variant ORDER BY variant_id"):
                data["stems"][iid].add(stem)
                o = json.loads(oj)
                if o:
                    data["options"][iid].add(" ".join(o))
        finally:
            conn.close()
        out("[M2] read %s (%s) sha256-bytes %s" % (os.path.basename(path), cv, sha))
    apply_closure_v2(data, out)
    return data


def item_stratum(data, iid):
    """An item's OWN modal (source, domain) vote (corpus rows, else ACTIVE responses, else quarantined ones; ties to the
    smallest pair): the stratum the BBH 5% mask reads (passage_closure), distinct from the component strata of the draw."""
    for v in (data["votes"], data["resp_votes"], data["q_votes"]):
        if v.get(iid):
            return _stratum(v[iid])
    _refuse("item %s has no stratum vote" % iid)


def u_digest(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def apply_closure_v2(data, out=print):
    """CK-CLOSE-v2 on the loaded corpora, BEFORE any stratum or draw: (U) the universe keeps an item iff it has a corpus
    source_row OR a response from an ACTIVE model; the excluded items leave data["items"] and data["units"] and are listed
    in data["excluded_u"] (K1 asserted here: none carries a row or an active response); (P, O, D) passage_closure's edges
    over the universe become union-find families "P:a|b" / "O:a|b" / "D:a|b" (both endpoints), so the family-crossing
    check of condition 3 covers them too. The full pre-U item set is kept in data["all_items"] for the DEV-SIM print."""
    data["all_items"] = dict(data["items"])
    keep = {i for i in data["items"] if data["votes"].get(i) or data["resp_votes"].get(i)}
    excluded = sorted(set(data["items"]) - keep)
    for i in excluded:
        if data["votes"].get(i) or data["resp_votes"].get(i):
            _refuse("U: excluded item %s carries a corpus row or an active response" % i)
    data["excluded_u"] = excluded
    data["families_pre_u"] = list(data["families"])
    data["items"] = {i: data["items"][i] for i in sorted(keep)}
    data["units"] = {u: d for u, d in data["units"].items() if d["item"] in keep}
    data["families"] = [(f, i) for f, i in data["families"] if i in keep]
    items = {}
    for i in data["items"]:
        st = item_stratum(data, i)
        items[i] = {"stems": sorted(data["stems"][i]), "options": sorted(data["options"][i]), "source": st[0], "stratum": st}
    r = C.pc.compute_edges(items, C.split_side.stem_key, out=out)
    data["closure_v2"] = r
    for kind in ("P", "O", "D"):
        for a, b in r["edges"][kind]:
            fam = "%s:%s|%s" % (kind, a, b)
            data["families"].append((fam, a))
            data["families"].append((fam, b))
    out("[M2] CK-CLOSE-v2 U: %d items excluded (no corpus source_row, no ACTIVE response), universe %d; digest"
        " sha256(sorted ids, LF) %s" % (len(excluded), len(keep), u_digest(excluded)))
    out("[M2] CK-CLOSE-v2 edges over the universe: P %d, O %d, D %d; residual 15-19-token band (counted, never joined)"
        " P %d / O %d; shingle collisions P %d / O %d; edge-set sha16 %s (N %d, K %d, R %d, BBH %.0f%% of the item's"
        " stratum, pair rule %s)"
        % (len(r["edges"]["P"]), len(r["edges"]["O"]), len(r["edges"]["D"]), r["band_15_19"]["P"], r["band_15_19"]["O"],
           r["collisions"]["P"], r["collisions"]["O"], r["edge_set_sha16"], C.pc.N, C.pc.K, C.pc.R,
           100 * C.pc.BBH_SHARE, C.pc.PAIR_RULE))
    for ch in ("P", "O"):
        t = r["df_table"][ch]
        out("[M2]   df table %s (distinct items holding a shingle -> number of distinct shingles; %d shingles): %s; >12: %d"
            % (ch, r["distinct_shingles"][ch], ", ".join("%d:%d" % (k, t[k]) for k in sorted(t) if k <= 12),
               sum(v for k, v in t.items() if k > 12)))
    if any(r["collisions"].values()):
        _refuse("shingle-key collisions %s" % r["collisions"])
    return data


def _stratum(votes):
    if not votes:
        return None
    return sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def compute(data, seed, eval_ratio=DEFAULT_EVAL_RATIO, gate_ratio=DEFAULT_GATE_RATIO):
    """The pure draw: components, strata, sides. Deterministic in (data, seed, ratios)."""
    if not (0 < eval_ratio < 1 and 0 <= gate_ratio < 1 and eval_ratio + gate_ratio < 1):
        _refuse("ratios out of range: eval %r gate %r" % (eval_ratio, gate_ratio))
    # CK-CLOSE-v2 K3: D (and every edge) JOINS items and never re-keys them: each item's key must still be its own
    # norm-v1 stem_key, i.e. the key its id was made from
    rekeyed = [i for i, sk in data["items"].items() if i != "i:" + sk]
    if rekeyed:
        _refuse("%d item(s) carry a key other than their own stem_key (e.g. %s): a closure edge must not change a key"
                % (len(rekeyed), rekeyed[0]))
    uf = _UF()
    for iid in data["items"]:
        uf.find(("i", data["items"][iid]))
    for fam, iid in data["families"]:
        uf.union(("f", fam), ("i", data["items"][iid]))
    members = defaultdict(list)
    for iid in sorted(data["items"]):
        members[uf.find(("i", data["items"][iid]))].append(iid)
    comp_of, comps = {}, {}
    for root, its in members.items():
        cid = "c:" + min(data["items"][i] for i in its)
        comps[cid] = sorted(its)
        for i in its:
            comp_of[i] = cid
    strata = {}
    multi = 0
    for cid, its in comps.items():
        v = Counter()
        for i in its:
            v.update(data["votes"].get(i, {}))
        if not v:
            for i in its:
                v.update(data["resp_votes"].get(i, {}))
        if not v:
            for i in its:
                v.update(data["q_votes"].get(i, {}))
        st = _stratum(v)
        if st is None:
            _refuse("component %s has no stratum vote" % cid)
        strata[cid] = (st, len(v))
        multi += len(v) > 1
    by_stratum = defaultdict(list)
    for cid in comps:
        by_stratum[strata[cid][0]].append(cid)
    side_of, rank_of = {}, {}
    for st in sorted(by_stratum):
        cids = by_stratum[st]
        for cid in cids:
            rank_of[cid] = hashlib.sha256((DRAW_TAG + C.US + seed + C.US + cid).encode("utf-8")).hexdigest()
        cids.sort(key=lambda c: rank_of[c])
        n = len(cids)
        n_eval = int(eval_ratio * n + 0.5)
        n_gate = min(int(gate_ratio * n + 0.5), n - n_eval)
        for k, cid in enumerate(cids):
            side_of[cid] = EVAL if k < n_eval else GATE if k < n_eval + n_gate else TRAIN
    return {"components": comps, "comp_of": comp_of, "strata": strata, "by_stratum": dict(by_stratum),
            "side_of": side_of, "rank_of": rank_of, "multi_stratum": multi}


def _shape(res):
    comps = res["components"]
    largest = defaultdict(int)
    for cid, its in comps.items():
        src = res["strata"][cid][0][0]
        largest[src] = max(largest[src], len(its))
    hist = len(res["by_stratum"].get(("MMLU_PRO", "history"), []))
    return {"components": len(comps), "largest": max(len(v) for v in comps.values()),
            "largest_per_source": dict(sorted(largest.items())), "multi_stratum": res["multi_stratum"],
            "history_components": hist}


def v2_report(data, res, out=print):
    """K5 prints and the K4 edge check on the drawn split; returns the figures (recorded in the split's meta)."""
    side_item = {i: res["side_of"][res["comp_of"][i]] for i in data["items"]}
    crossing = {k: sum(1 for a, b in data["closure_v2"]["edges"][k] if side_item[a] != side_item[b]) for k in "POD"}
    if any(crossing.values()):
        _refuse("closure edges crossing sides: %s" % crossing)
    shape = _shape(res)
    kish = {}
    for src in sorted({res["strata"][c][0][0] for c in res["components"]}):
        sizes = [len(its) for c, its in res["components"].items()
                 if res["strata"][c][0][0] == src and res["side_of"][c] == EVAL]
        n = sum(sizes)
        kish[src] = {"eval_items": n, "eval_components": len(sizes),
                     "kish": (sum(s * s for s in sizes) / n) if n else float("nan")}
    ev = sum(len(its) for c, its in res["components"].items() if res["side_of"][c] == EVAL)
    share = ev / len(data["items"])
    out("[M2] CK-CLOSE-v2 K4: closure edges crossing the sides P %d / O %d / D %d (must be 0); every component is on one"
        " side by construction" % (crossing["P"], crossing["O"], crossing["D"]))
    out("[M2] CK-CLOSE-v2 K5 (after U): components %d, largest %d, largest per source %s, multi-stratum components %d,"
        " MMLU-Pro history components %d; EVAL share of items %.4f"
        % (shape["components"], shape["largest"], json.dumps(shape["largest_per_source"]), shape["multi_stratum"],
           shape["history_components"], share))
    out("[M2]   Kish per source over EVAL ITEMS, clusters = components (sum n^2 / n, an UPPER bound): %s"
        % ", ".join("%s %.3f (%d items / %d components)" % (s, v["kish"], v["eval_items"], v["eval_components"])
                    for s, v in kish.items()))
    # the DEV-SIM figures are BEFORE U: reproduce them on the full item set (edges over all items, the pre-U families)
    items_all = {}
    for i in sorted(data["all_items"]):
        st = item_stratum(data, i)
        items_all[i] = {"stems": sorted(data["stems"][i]), "options": sorted(data["options"][i]), "source": st[0], "stratum": st}
    r_all = C.pc.compute_edges(items_all, C.split_side.stem_key, out=lambda s: None)
    fam = list(data["families_pre_u"])
    for kind in ("P", "O", "D"):
        for a, b in r_all["edges"][kind]:
            fam += [("%s:%s|%s" % (kind, a, b), a), ("%s:%s|%s" % (kind, a, b), b)]
    pre = _shape(compute(dict(data, items=data["all_items"], families=fam), "DEV-SIM-SHAPE-ONLY"))
    out("[M2]   BEFORE U, reproduced here (edges over all %d items): components %d, largest %d, per source %s,"
        " multi-stratum %d, history %d" % (len(items_all), pre["components"], pre["largest"],
                                           json.dumps(pre["largest_per_source"]), pre["multi_stratum"], pre["history_components"]))
    out("[M2]   DEV-SIM of the registration (NOT OF RECORD, before U): components %d, largest %d (BBH), MMLU-Pro largest %d,"
        " history %d, multi-stratum %d; Kish EVAL MMLU-Pro %.3f / BBH %.2f / MuSR %.2f; EVAL share %.4f-%.4f over 20 DEV seeds"
        % (DEV_SIM["components_before_u"], DEV_SIM["largest_before_u"], DEV_SIM["largest_mmlu_pro_before_u"],
           DEV_SIM["history_components_before_u"], DEV_SIM["multi_stratum_before_u"], DEV_SIM["kish_eval"]["MMLU_PRO"],
           DEV_SIM["kish_eval"]["BBH"], DEV_SIM["kish_eval"]["MUSR"], DEV_SIM["eval_share_band"][0], DEV_SIM["eval_share_band"][1]))
    return {"u_count": len(data["excluded_u"]), "u_digest": u_digest(data["excluded_u"]),
            "edges": {k: len(v) for k, v in data["closure_v2"]["edges"].items()},
            "band_15_19": data["closure_v2"]["band_15_19"], "edge_set_sha16": data["closure_v2"]["edge_set_sha16"],
            "crossing": crossing, "after_u": shape, "eval_share": share, "kish_eval_items": kish, "before_u": pre,
            "before_u_edge_set_sha16": r_all["edge_set_sha16"]}


def merge_pool(pools, pid, scope, n_comp, n_items):
    """Add one scope's pool to pools {pid: ([scopes], n_components, {scope: n_items})}. Two scopes with the same component
    list share one id and are MERGED into one row (never overwritten); an id naming two component counts is refused."""
    if pid in pools:
        if pools[pid][1] != n_comp:
            _refuse("pool id %s names two different component lists" % pid)
        pools[pid][0].append(scope)
        pools[pid][2][scope] = n_items
    else:
        pools[pid] = ([scope], n_comp, {scope: n_items})
    return pools


def pool_id(component_ids, dev):
    h = hashlib.sha256("\n".join(sorted(component_ids)).encode("utf-8")).hexdigest()[:16]
    return ("pv2dev_" if dev else "pv2_") + h


def closure_checks(data, res, out=print):
    """The CK-CLOSE-v1 checks on the drawn split, through content_closure (reused). REFUSES on any failure. Returns
    the printed figures.

    UNITS, NOT ITEMS (READY_archv2_ED D10, documented): every count printed here is over UNITS = the source rows of both
    corpora plus the response-only variants; an MMLU-Pro item present in both corpora is TWO units, and one item can have
    several units (twins, response-only renderings). "sentinel" counts units of EVAL items with no active-model response
    (on ED2: 382 units, which belong to fewer items, 249 by the reviewer's count). The pooled Kish figure counts an item
    once per unit and is an upper bound over units; the per-corpus lines are the ones a per-corpus board uses. Item
    counts are the ones printed by build_split ("items EVAL / GATE / TRAIN")."""
    units = data["units"]
    side_item = {i: res["side_of"][res["comp_of"][i]] for i in data["items"]}
    parts = defaultdict(lambda: {"gen": set(), "reserved": set(), "sentinel": set()})
    for uid, u in units.items():
        s = side_item[u["item"]]
        if s == EVAL:
            parts[u["corpus"]]["reserved" if u["judgeable"] else "sentinel"].add(uid)
        else:
            parts[u["corpus"]]["gen"].add(uid)
    text_of = {uid: u["text"] for uid, u in units.items()}
    r = C.cc.build_closure(dict(parts), text_of)
    moved = r["counts"]["n_moved"]
    out("[M2] CK-CLOSE-v1 condition 2 (global): one build_closure over %d corpora, %d units: gen %d, reserved %d, sentinel"
        " %d -> moved %d (must be 0)" % (len(parts), len(units), r["counts"]["n_gen"], r["counts"]["n_reserved"],
                                         r["counts"]["n_sentinel"], moved))
    if moved != 0:
        _refuse("build_closure moved %d generation-side units: the drawn split is not closed" % moved)
    gen = set().union(*(p["gen"] for p in parts.values()))
    reserved = set().union(*(p["reserved"] for p in parts.values()))
    sentinel = set().union(*(p["sentinel"] for p in parts.values()))
    C.cc.assert_content_disjoint(gen, reserved, sentinel, text_of, where="v2 split (condition 1: sentinels explicit)",
                                 out=lambda s: out("[M2] " + s))
    fam_sides = defaultdict(set)
    for fam, iid in data["families"]:
        fam_sides[fam].add(side_item[iid] == EVAL)
    crossing = sum(1 for s in fam_sides.values() if len(s) > 1)
    out("[M2] CK-CLOSE-v1 condition 3 (family): %d families (declared + legacy-qid), %d crossing the EVAL boundary"
        " (must be 0)" % (len(fam_sides), crossing))
    if crossing:
        _refuse("%d families cross the EVAL boundary" % crossing)
    ev_set = reserved | sentinel
    dropped = sum(1 for uid, u in units.items() if side_item[u["item"]] == EVAL and uid not in ev_set)
    if dropped:
        _refuse("%d units of EVAL items are missing from the held-out key set" % dropped)
    ev_units = sorted(ev_set)
    cl, st = C.cc.reserved_clusters(ev_units, text_of)
    b = st["by_key"]
    comp_sizes = Counter(res["comp_of"][units[u]["item"]] for u in ev_units)
    n = sum(comp_sizes.values())
    kish_comp = sum(v * v for v in comp_sizes.values()) / n if n else float("nan")
    out("[M2] CK-CLOSE-v1 condition 4 (cluster, never drop): %d EVAL units (%d judgeable + %d routing-only sentinels), %d"
        " dropped; clusters by key %d (ids in twin groups %d, max %d), Kish sum(n^2)/n %.4f -> n_eff(rho=1) %.1f; by"
        " component %d clusters, Kish %.4f -> n_eff(rho=1) %.1f [%s]"
        % (n, len(reserved), len(sentinel), dropped, b["n_clusters"], b["n_in_twin_groups"], b["max_cluster"], b["kish"],
           b["n_eff_rho1"], len(comp_sizes), kish_comp, n / kish_comp if n else float("nan"), st["bound"]))
    if len(cl) != n:
        _refuse("reserved_clusters returned %d cluster ids for %d EVAL units" % (len(cl), n))
    out("[M2]   (the pooled figure counts an MMLU-Pro item once per corpus that carries it; the per-corpus figures are"
        " the ones a per-corpus board uses)")
    per_corpus = {}
    for cv in sorted(parts):
        ev_c = sorted(parts[cv]["reserved"] | parts[cv]["sentinel"])
        if not ev_c:
            continue
        _cl, s_ = C.cc.reserved_clusters(ev_c, text_of)
        bk = s_["by_key"]
        csz = Counter(res["comp_of"][units[u]["item"]] for u in ev_c)
        kc = sum(v * v for v in csz.values()) / len(ev_c)
        per_corpus[cv] = {"eval_units": len(ev_c), "clusters_key": bk["n_clusters"], "kish_key": bk["kish"],
                          "clusters_component": len(csz), "kish_component": kc}
        out("[M2]   %-16s EVAL units %5d (judgeable %5d, sentinels %4d); clusters by key %5d, Kish %.4f -> n_eff(rho=1)"
            " %.1f; by component %5d, Kish %.4f -> n_eff(rho=1) %.1f"
            % (cv, len(ev_c), len(parts[cv]["reserved"]), len(parts[cv]["sentinel"]), bk["n_clusters"], bk["kish"],
               bk["n_eff_rho1"], len(csz), kc, len(ev_c) / kc))
    return {"per_corpus": per_corpus,"moved": moved, "gen": len(gen), "reserved": len(reserved), "sentinel": len(sentinel),
            "families": len(fam_sides), "families_crossing": crossing, "eval_units": n,
            "kish_key": b["kish"], "kish_component": kish_comp, "clusters_key": b["n_clusters"],
            "clusters_component": len(comp_sizes), "twin_group_ids": b["n_in_twin_groups"]}


SIDE_COLS = ("item_id", "component_id", "side", "stratum_source", "stratum_domain", "corpora")
SIDE_EXPORT_FORMAT = "taxoarena-side-export-v1"


def _side_rows_sha(rows):
    """ro.table_sha's rule applied to rows given in primary-key order (repr of the tuple + LF)."""
    h = hashlib.sha256()
    for r in rows:
        h.update((repr(tuple(r)) + "\n").encode("utf-8"))
    return h.hexdigest()


def export_side(split_path, out_path):
    """Write the sealed split's `side` table as evidence: UTF-8, LF, deterministic (item_id order), written ONCE (mode x).
    Line 1: '# <format> table_sha=<hex> rows=<n> split_sha256=<hex>'; line 2: the tab-separated header; then one row per
    item. Every value is TEXT; a tab or a newline inside a value is refused. Returns (table_sha, rows)."""
    split_sha = ro.file_sha256(split_path)
    sp = ro.open_ro(split_path, require_sealed=True)
    try:
        cols = [r[1] for r in sp.execute("PRAGMA table_info(side)")]
        if tuple(cols) != SIDE_COLS:
            _refuse("side table columns %s != %s" % (cols, SIDE_COLS))
        db_sha, n = ro.table_sha(sp, "side")
        rows = sp.execute("SELECT %s FROM side ORDER BY item_id" % ", ".join(SIDE_COLS)).fetchall()
    finally:
        sp.close()
    for r in rows:
        for v in r:
            if not isinstance(v, str) or "\t" in v or "\n" in v or "\r" in v:
                _refuse("side export: value %r is not a tab/newline-free TEXT" % (v,))
    if _side_rows_sha(rows) != db_sha:
        _refuse("side export: recomputed sha differs from ro.table_sha")
    with open(out_path, "x", encoding="utf-8", newline="\n") as f:
        f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (SIDE_EXPORT_FORMAT, db_sha, n, split_sha))
        f.write("\t".join(SIDE_COLS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    return db_sha, n


def verify_side_export(export_path, split_path=None):
    """Recompute the table sha from the exported TEXT and compare it with the header and, when given, with the sealed
    DB's `side` table (ro.table_sha). REFUSES on any difference. Returns (table_sha, rows)."""
    with open(export_path, "rb") as f:
        data = f.read()
    if b"\r" in data:
        _refuse("side export %s is not LF-only" % export_path)
    lines = data.decode("utf-8").split("\n")
    if lines[-1] != "":
        _refuse("side export %s does not end with LF" % export_path)
    head = lines[0].split()
    if len(head) != 5 or head[1] != SIDE_EXPORT_FORMAT:
        _refuse("side export %s: bad header %r" % (export_path, lines[0]))
    hdr = dict(x.split("=", 1) for x in head[2:])
    if lines[1].split("\t") != list(SIDE_COLS):
        _refuse("side export %s: bad column header" % export_path)
    rows = [tuple(ln.split("\t")) for ln in lines[2:-1]]
    if any(len(r) != len(SIDE_COLS) for r in rows) or rows != sorted(rows, key=lambda r: r[0]):
        _refuse("side export %s: malformed or unordered rows" % export_path)
    sha = _side_rows_sha(rows)
    if sha != hdr["table_sha"] or len(rows) != int(hdr["rows"]):
        _refuse("side export %s: text sha %s / rows %d != header %s / %s" % (export_path, sha, len(rows), hdr["table_sha"], hdr["rows"]))
    if split_path is not None:
        sp = ro.open_ro(split_path, require_sealed=True)
        try:
            db_sha, n = ro.table_sha(sp, "side")
        finally:
            sp.close()
        if (db_sha, n) != (sha, len(rows)):
            _refuse("side export %s: text sha %s != sealed DB table_sha %s" % (export_path, sha, db_sha))
        if ro.file_sha256(split_path) != hdr["split_sha256"]:
            _refuse("side export %s: split_sha256 in the header is not the split file's" % export_path)
    return sha, len(rows)


def check_draw(seed, registration):
    """The draw guard, by VALUE (READY_archv2_ED D1). A DEV seed ("DEV-...") runs without a registration and is labelled
    "DEV, NOT OF RECORD"; a DEV seed WITH a registration is refused (a DEV draw is never registered). Any other seed runs
    ONLY as the exact (registration, seed) pair pinned in REGISTERED_DRAWS; a wrong seed, a wrong or missing entry, or any
    other string is REFUSED. Returns (dev, label)."""
    if C.is_dev_seed(seed):
        if registration:
            _refuse("a DEV seed (%r) is never registered; drop --registration %r" % (seed, registration))
        return True, C.OF_RECORD_DEV
    if registration in RETIRED_DRAWS or seed in RETIRED_DRAWS.values():
        _refuse("draw %r / seed %r already ran and is RETIRED (never reused)" % (registration, seed))
    if not registration:
        _refuse("seed %r is not a DEV seed: a real draw needs --registration naming its pinned entry" % seed)
    pinned = REGISTERED_DRAWS.get(registration)
    if pinned is None:
        _refuse("registration %r is not a pinned draw (pinned: %s)" % (registration, ", ".join(sorted(REGISTERED_DRAWS))))
    if seed != pinned:
        _refuse("registration %r pins the seed %r; %r is refused" % (registration, pinned, seed))
    return False, "registered seed (%s)" % registration


def build_split(corpus_paths, out_dir, seed, registration=None, eval_ratio=DEFAULT_EVAL_RATIO,
                gate_ratio=DEFAULT_GATE_RATIO, out=print):
    dev, label = check_draw(seed, registration)
    out("[M2] seed %r -> %s; rule %s; eval ratio %.2f, gate ratio %.2f" % (seed, label, RULE, eval_ratio, gate_ratio))
    data = load_corpora(corpus_paths, out)
    res = compute(data, seed, eval_ratio, gate_ratio)
    comps, side_of = res["components"], res["side_of"]
    n_items = len(data["items"])
    out("[M2] items %d (global over %d corpora), components %d (%d merged by a family edge, %d items in them), %d"
        " components voting in more than one stratum"
        % (n_items, len(data["corpora"]), len(comps), sum(1 for v in comps.values() if len(v) > 1),
           sum(len(v) for v in comps.values() if len(v) > 1), res["multi_stratum"]))
    checks = closure_checks(data, res, out)
    v2 = v2_report(data, res, out)
    checks["v2"] = v2
    tag = "DEV" if dev else "REG"
    safe_seed = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in seed)
    out_path = os.path.join(out_dir, "split_v2_%s_%s.db" % (tag, safe_seed))
    conn = ro.create_new(out_path)
    conn.executescript(DDL)
    for cid in sorted(comps):
        (ss_, sd_), nv = res["strata"][cid]
        conn.execute("INSERT INTO component VALUES (?,?,?,?,?,?,?)",
                     (cid, len(comps[cid]), ss_, sd_, nv, res["rank_of"][cid], side_of[cid]))
    for iid in sorted(data["items"]):
        cid = res["comp_of"][iid]
        (ss_, sd_), _nv = res["strata"][cid]
        conn.execute("INSERT INTO side VALUES (?,?,?,?,?,?)",
                     (iid, cid, side_of[cid], ss_, sd_, ",".join(sorted(data["item_corpora"][iid]))))
    lines = []
    tot = Counter()
    for st in sorted(res["by_stratum"]):
        cids = res["by_stratum"][st]
        c = Counter(side_of[x] for x in cids)
        ni = sum(len(comps[x]) for x in cids)
        ne = sum(len(comps[x]) for x in cids if side_of[x] == EVAL)
        conn.execute("INSERT INTO stratum VALUES (?,?,?,?,?,?,?,?)", (st[0], st[1], len(cids), ni, c[EVAL], c[GATE], c[TRAIN], ne))
        lines.append("    %-12s %-38s components %5d  EVAL %5d  GATE %4d  TRAIN %5d  (items %5d, EVAL items %5d)"
                     % (st[0], st[1][:38], len(cids), c[EVAL], c[GATE], c[TRAIN], ni, ne))
        tot.update(c)
    out("[M2] per stratum (source, domain): %d strata" % len(res["by_stratum"]))
    for ln in lines:
        out(ln)
    ev_items = sum(len(comps[x]) for x in comps if side_of[x] == EVAL)
    out("[M2] totals: components EVAL %d / GATE %d / TRAIN %d; items EVAL %d / GATE %d / TRAIN %d (EVAL share of items %.4f)"
        % (tot[EVAL], tot[GATE], tot[TRAIN], ev_items, sum(len(comps[x]) for x in comps if side_of[x] == GATE),
           sum(len(comps[x]) for x in comps if side_of[x] == TRAIN), ev_items / n_items))
    ev_c = [x for x in comps if side_of[x] == EVAL]
    # a pool id is the hash of its component list, so two scopes with the SAME EVAL component list share ONE id (under U,
    # every EVAL component has a member in the union corpus): the scopes are MERGED into the one row, never overwritten
    # [FIXED 2026-09-24: the dict was keyed by id and the second scope silently replaced the first]
    pools = {}
    merge_pool(pools, pool_id(ev_c, dev), "all corpora", len(ev_c), ev_items)
    for cinfo in data["corpora"]:
        cv = cinfo["corpus_version"]
        cc_ = sorted({x for x in ev_c if any(cv in data["item_corpora"][i] for i in comps[x])})
        merge_pool(pools, pool_id(cc_, dev), cv, len(cc_), sum(1 for x in cc_ for i in comps[x] if cv in data["item_corpora"][i]))
    for i in data["excluded_u"]:
        conn.execute("INSERT INTO excluded_u VALUES (?)", (i,))
    for kind in ("P", "O", "D"):
        for a, b in data["closure_v2"]["edges"][kind]:
            conn.execute("INSERT INTO closure_edge VALUES (?,?,?)", (kind, a, b))
    for pid in sorted(pools):
        scopes, ncomp, nitems = pools[pid]
        conn.execute("INSERT INTO pool VALUES (?,?,?,?)", (pid, " + ".join(scopes), ncomp, json.dumps(nitems, sort_keys=True)))
        out("[M2] new pool id %s  scope %s: EVAL components %d, EVAL items %s  [%s]"
            % (pid, " + ".join(scopes), ncomp, ", ".join("%s %d" % kv for kv in nitems.items()), label))
    meta = {"of_record": label, "seed": seed, "registration": registration or "", "rule": RULE,
            "normaliser": C.split_side.NORMALISER_VERSION, "key_rule": C.split_side.KEY_RULE, "draw_tag": DRAW_TAG,
            "eval_ratio": repr(eval_ratio), "gate_ratio": repr(gate_ratio),
            "split_fn_blob": ro.git_blob_lf(os.path.abspath(__file__)), "content_closure_blob": C.PINS["content_closure"],
            "split_side_blob": C.PINS["split_side"], "corpora": json.dumps(data["corpora"], sort_keys=True),
            "checks": json.dumps(checks, sort_keys=True), "pools": json.dumps({k: list(v) for k, v in pools.items()}, sort_keys=True),
            "passage_closure_blob": C.PINS["passage_closure"], "u_count": str(len(data["excluded_u"])),
            "u_digest": u_digest(data["excluded_u"]), "edge_set_sha16": data["closure_v2"]["edge_set_sha16"],
            "closure_params": json.dumps({"N": C.pc.N, "K": C.pc.K, "R": C.pc.R, "BBH_SHARE": C.pc.BBH_SHARE,
                                          "PAIR_RULE": C.pc.PAIR_RULE}, sort_keys=True)}
    for k in sorted(meta):
        conn.execute("INSERT INTO meta VALUES (?,?)", (k, str(meta[k])))
    conn.commit()
    sealed = ro.seal(conn, out_path, "split_v2 %s seed %s" % (label, seed))
    out("[M2] SEALED %s sha256-bytes %s" % (os.path.basename(out_path), sealed["sha256_bytes"]))
    return {"path": out_path, "kind": "split_v2", "seed": seed, "of_record": label, "checks": checks,
            "pools": {k: list(v) for k, v in pools.items()}, **sealed}
