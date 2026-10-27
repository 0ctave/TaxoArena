"""data_v2.gates: the zero-call gates of ARCH-v2 E-D that can run now (SYNTHESIS §4 G1, G2, G4, G5), and the selftest.

    python tools/analysis/data_v2/gates.py --selftest                  # synthetic, opens NO DB of record; python and -O
    python tools/analysis/data_v2/gates.py --build-dir data_v2/<label>  # the real gates on a built DEV directory
                                                                        # (TAXOARENA_DATA_ROOT = the main checkout)

Each gate prints one PASS / FAIL line per check and a final "[GATE Gn] PASS" or a refusal: raise SystemExit, never an
assert (the gates hold under python -O). Nothing here posts a call or writes into an existing DB: the sources are opened
through data_v2.ro.open_ro, and G5 writes only a NEW scratch verdict DB in a temporary directory.

G1  ingestion bijection (data V1): every upstream corpus row and every response row maps to exactly one source_row /
    response, and its variant (seen_ck), recomputed from the row's OWN content, equals the stored one; the counts of
    record: mmlu_pro 12,000 / union corpus_questions 21,606 / MMLU-Pro eval_results 560,379 (union eval_results 388,908
    printed too); corpus items 11,609 / 20,535; GPQA 546. A difference is REPORTED (MISMATCH, exit 1), never tuned.
G2  closure (data V2): the sealed side table is re-derived from the corpora and the seed and must agree item for item;
    content_closure.build_closure moves 0 units, assert_content_disjoint passes with the sentinels explicit, 0 families
    cross the boundary; the physical views: stem keys(gen_view) intersect EVAL keys = 0. POSITIVE CONTROL: on the OLD p2dca
    split (id file experiment_configs/reserved_pool_frozen_p2dca.json, re-hashed to p2dca21ab5f4ef3ae), rebuilt from the
    corpus_v2 alias rows, the judgeable ids with a generation-side twin are 37 on exact text and 70 on norm-v1, the
    engine closure moves 171, and the guard REFUSES (a guard reporting 0 would be vacuous).
    (G2's "both languages" clause needs the Kotlin half, CK-CLOSE-V1-IMPL (b), scheduled after the long runs: NOT RUN.)
G4  loader denial, both branches executed (data V4): open_generation admits construct and refuses judge; open_eval admits
    route and refuses construct; a view passed to the wrong opener is refused by its own meta; an unknown stage is refused;
    assert_not_eval refuses an EVAL text and admits a TRAIN text.
G5  append-only (data V5): UPDATE / DELETE abort on every table; a schedule insert after the first attempt aborts; the
    relaunch anti-join posts exactly the pending slots, never a cached CONTENT_FILTER, and NOTHING when complete; the same
    body in two draws is stored twice (R7); a sealed run refuses a writer.
"""
import glob
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "data_v2"
    import data_v2  # noqa: F401

from . import common as C  # noqa: E402
from . import independent, ingest, ro, split, verdicts, views  # noqa: E402

P2DCA = "p2dca21ab5f4ef3ae"
P2DCA_ID_FILE = os.path.join(C.ROOT, "experiment_configs", "reserved_pool_frozen_p2dca.json")
P2DCA_RECORD = {"exact": 37, "norm_v1": 70, "moved": 171}
# READY_archv2_ED D2: the side table of the synthetic fixture under the seed "DEV-selftest" (ro.table_sha of the sealed
# split's `side` table), pinned as a literal so a draw that ignores the seed or changes the rounding fails the selftest.
# It changes only when the fixture or the draw rule changes, and then by a reviewed edit of this line.
# [RE-PINNED 2026-09-24 for CK-CLOSE-v2: the fixture gained the K3 cases and the rule gained U / P / O / D; the v1 value
# was 292c6fa70f9751af67deb839b4cb2cd2e05d3679f5608e4a5f953a1face1f524 (127 rows)]
# [RE-PINNED 2026-09-24 for READY_ck_close_v2 D2: the fixture gained a second BBH task, the df-6 group with a two-variant
# item and the upper-case pair; the value before was de2fb10baecbf58a1521c68f35ded4ec23c9be7b69b734086a6f342ace4c12d3 (167 rows)]
GOLDEN_FIXTURE_SIDE_SHA = "82f3ba14ed85eeb219c08562fc6e2e8174cb777a76f61aca7f9b5663786be569"
def _w(tag, n, start=0):
    return " ".join("%s%02d" % (tag, i) for i in range(start, start + n))


# CK-CLOSE-v2 K3 fixture texts (every case uses its own words, so each shared run has exactly the stated length)
K3 = {
    "P20a": "ua1 ua2 %s ua3" % _w("pa", 20), "P20b": "ub1 %s ub2 ub3" % _w("pa", 20),          # 20-token run: JOINED
    "P19a": "uc1 %s uc2" % _w("pb", 19), "P19b": "ud1 %s ud2" % _w("pb", 19),                  # 19-token run: refused
    "PMa": "ue1 %s ue2" % _w("pm", 24), "PMb": "uf1 %s uf2" % _w("pm", 24),                    # 24 tokens, but pm08-pm15
    "D1": "%s 25\\textdegree C %s" % (_w("dl", 12), _w("dr", 12)),                             # is held by 7 items: masked
    "D2": "%s 25 °C %s" % (_w("dl", 12), _w("dr", 12)),
    "D3": "%s 25�C %s" % (_w("dl", 12), _w("dr", 12)),
}
K3_MMLU_ROWS = [(K3["P20a"], ["opt a", "opt b"]), (K3["P20b"], ["opt a", "opt b"]),
                (K3["P19a"], ["opt a", "opt b"]), (K3["P19b"], ["opt a", "opt b"]),
                (K3["PMa"], ["opt a", "opt b"]), (K3["PMb"], ["opt a", "opt b"])]
# the five other holders of the masked 8-gram (pm08-pm15 in the stems; oq08-oq15 in the options): df 7 > R 6
K3_MMLU_ROWS += [("ug%d %s uh%d" % (k, _w("pm", 8, 8), k), [_w("oq", 8, 8), "ui%d" % k]) for k in range(5)]
K3_MMLU_ROWS += [("Options case E?", [_w("oa", 10), _w("ob", 10)]), ("Options case F?", [_w("oa", 10), _w("ob", 10)]),  # O: 20
                 ("Options case G?", [_w("oc", 10), _w("od", 9)]), ("Options case H?", [_w("oc", 10), _w("od", 9)]),    # O: 19
                 ("Options case I?", [_w("oq", 24)]), ("Options case J?", [_w("oq", 24)])]                              # O: masked
K3_MMLU_ROWS += [(K3["D1"], ["opt a", "opt b"]), (K3["D2"], ["opt a", "opt b"]), (K3["D3"], ["opt a", "opt b"])]
# READY_ck_close_v2 D2 (fixture gaps):
#  - df EXACTLY R = 6 is unmasked (kills df >= R, M3c): six items hold one 20-token run; one of the six is an item with
#    TWO variants (raw stems differing only in ASCII case and whitespace, so norm-v1 gives one item; different options,
#    so two variants): counted over TEXTS its run would have df 7 and be masked (kills df-over-variants, M2);
#  - an UPPER-CASE rendering of a lower-case run, as two distinct items, joined only through casefold (kills M11)
K3.update({"UPa": "ua9 %s zu1" % _w("pu", 20).upper(), "UPb": "ub9 %s zu2" % _w("pu", 20),
           "V6a": "VV1 %s VV2" % _w("ps", 20), "V6b": "vv1   %s   vv2" % _w("ps", 20)})
K3_MMLU_ROWS += [(K3["UPa"], ["opt a", "opt b"]), (K3["UPb"], ["opt a", "opt b"]),
                 (K3["V6a"], ["opt a", "opt b"]), (K3["V6b"], ["opt c", "opt d"])]
K3_DF6_OTHERS = ["sx%d %s sy%d" % (k, _w("ps", 20), k) for k in range(5)]
K3_MMLU_ROWS += [(t, ["opt a", "opt b"]) for t in K3_DF6_OTHERS]
# a SECOND BBH task (30 items; 5% = 1.5 items): its pair k 10-11 shares a run held by 2 of 30 (MASKED in its task),
# while a source-wide mask (70 BBH items, 3.5) would unmask it, and would also unmask task 1's 3-of-40 triple (kills M3)
K3_BBH2_STEMS = {10: "en1 %s en2" % _w("bw", 20), 11: "eo1 %s eo2" % _w("bw", 20)}
K3_BBH_STEMS = {30: "ej1 %s ej2" % _w("bj", 20), 31: "ek1 %s ek2" % _w("bj", 20)}
K3_BBH_STEMS.update({k: "el%d %s em%d" % (k, _w("bt", 20), k) for k in (32, 33, 34)})
K3_QUARANTINED_ONLY = "A quarantined only question nobody active answered qz01?"
RECORD_G1 = {"mmlu-pro-v2": {"source_rows": 12000, "items_corpus": 11609, "responses": 560379},
             "mc6-2026-09-11": {"source_rows": 21606, "items_corpus": 20535, "gpqa_items": 546, "responses": 388908}}


class Gate:
    def __init__(self, name, out=print):
        self.name, self.out, self.fails = name, out, []

    def check(self, what, ok, detail=""):
        ok = bool(ok)
        self.out("  [%s] %-4s %s%s" % (self.name, "PASS" if ok else "FAIL", what, (" (" + detail + ")") if detail else ""))
        if not ok:
            self.fails.append(what)
        return ok

    def close(self):
        if self.fails:
            self.out("[GATE %s] FAIL: %d check(s) failed: %s" % (self.name, len(self.fails), "; ".join(self.fails)))
            raise SystemExit(1)
        self.out("[GATE %s] PASS" % self.name)
        return 0


# ── G1 ──────────────────────────────────────────────────────────────────────────────────────

def g1_corpus(corpus_path, data_root, gate, record=None):
    cm = ro.open_ro(corpus_path, require_sealed=True)
    try:
        meta = dict(cm.execute("SELECT key, value FROM meta"))
        cv = meta["corpus_version"]
        spec = ingest.SPECS[cv]
        src_path = os.path.join(data_root, spec["db"])
        src_sha = ro.file_sha256(src_path)
        gate.check("%s: source DB unchanged since the build (sha256-bytes %s)" % (cv, src_sha[:16]),
                   src_sha == meta["source_db_sha256_bytes"], "built from %s" % meta["source_db_sha256_bytes"][:16])
        stored_rows = {rid: vid for rid, vid in cm.execute("SELECT source_row_id, variant_id FROM source_row")}
        stored_resp = {x: ck for x, ck in cm.execute("SELECT response_id, seen_ck FROM response")}
        row_opt = dict(cm.execute("SELECT source_row_id, options_ordered_sha FROM source_row"))
        resp_opt = dict(cm.execute("SELECT response_id, options_ordered_sha FROM response"))
        variants = {v: i for v, i in cm.execute("SELECT variant_id, item_id FROM variant")}
        items = {i: o for i, o in cm.execute("SELECT item_id, origin FROM item")}
        gpqa_items = cm.execute("SELECT COUNT(DISTINCT item_id) FROM item_subset").fetchone()[0]
        opt_bad = 0
        opt_keys = [s for (s,) in cm.execute("SELECT options_ordered_sha FROM options_ordered")]
        for s in opt_keys:
            try:
                C.options_raw(cm, s)
            except SystemExit:
                opt_bad += 1
        contracts = {c for (c,) in cm.execute("SELECT DISTINCT contract_id FROM variant")}
        try:
            C.guard_retired(cm, corpus_path)
            retired_ok = True
        except SystemExit:
            retired_ok = False
        refs = {}
        for vint, key in cm.execute("SELECT vintage, source_key FROM reference UNION ALL"
                                    " SELECT vintage, source_key FROM reference_unresolved"):
            refs.setdefault(vint, Counter())[key] += 1
        ref_how = {}
        for vint, how, n in cm.execute("SELECT vintage, resolution, COUNT(*) FROM reference GROUP BY 1, 2"):
            ref_how.setdefault(vint, {})[how] = n
        for vint, n in cm.execute("SELECT vintage, COUNT(*) FROM reference_unresolved GROUP BY 1"):
            ref_how.setdefault(vint, {})["unresolved"] = n
    finally:
        cm.close()
    gate.check("%s: %d content-addressed option lists, each hashing back to its key (%d bad)" % (cv, len(opt_keys), opt_bad),
               opt_bad == 0 and len(opt_keys) > 0)
    gate.check("%s: variant contracts %s all in the closed list" % (cv, sorted(contracts)), contracts <= set(ingest.CONTRACTS))
    gate.check("%s: the response table carries no retired column" % cv, retired_ok)
    for rs in ingest.LEGACY_REFERENCES.get(cv, ()):
        rp = os.path.join(data_root, rs["db"])
        rc = ro.open_ro(rp)
        try:
            legacy = ["qid:%d" % q for (q,) in rc.execute("SELECT question_id FROM answers")]
        finally:
            rc.close()
        got = refs.get(rs["vintage"], Counter())
        un = sum(1 for k in legacy if k not in got)
        ex = sum(1 for k in got if k not in set(legacy))
        dbl = sum(1 for v in got.values() if v > 1)
        gate.check("%s: legacy references %s: %d cache rows -> reference + unresolved 1:1 (unmapped %d, extra %d, doubly"
                   " mapped %d) %s" % (cv, rs["vintage"], len(legacy), un, ex, dbl,
                                       json.dumps(dict(sorted(ref_how.get(rs["vintage"], {}).items())))),
                   un == 0 and ex == 0 and dbl == 0)
    keys = C.KeyCache()
    src = ro.open_ro(src_path)
    try:
        exp_rows, dup_rows, bad_ck, bad_opt = {}, 0, 0, 0
        for r in spec["source_rows"](src):
            rid = C.source_row_id(cv, r["table"], r["upstream_pk"])
            if rid in exp_rows:
                dup_rows += 1
            vid, _o = keys.variant(r["text"], r["options_json"], r["contract"])
            exp_rows[rid] = vid
            bad_ck += stored_rows.get(rid, vid) != vid
            bad_opt += row_opt.get(rid, "") != C.options_ordered_sha(r["options_json"])
        exp_resp, dup_resp, bad_seen = {}, 0, 0
        for r in spec["responses"](src):
            x = C.response_id(cv, r["model"], r["legacy_qid"])
            if x in exp_resp:
                dup_resp += 1
            vid, _o = keys.variant(r["text"], r["options_json"], r["contract"])
            exp_resp[x] = vid
            bad_seen += stored_resp.get(x, vid) != vid
            bad_opt += resp_opt.get(x, "") != C.options_ordered_sha(r["options_json"])
    finally:
        src.close()
    gate.check("%s: every source row and response points to the options list of its OWN verbatim options_json (%d differ;"
               " the rows' lists are rebuilt verbatim through data_v2.common.options_raw)" % (cv, bad_opt), bad_opt == 0)
    rec = record if record is not None else RECORD_G1.get(cv, {})
    un_r = len(set(exp_rows) - set(stored_rows)); ex_r = len(set(stored_rows) - set(exp_rows))
    un_x = len(set(exp_resp) - set(stored_resp)); ex_x = len(set(stored_resp) - set(exp_resp))
    gate.check("%s: %d upstream corpus rows -> %d source rows, 1:1 (unmapped %d, extra %d, doubly mapped %d, variant"
               " differs %d)" % (cv, len(exp_rows) + dup_rows, len(stored_rows), un_r, ex_r, dup_rows, bad_ck),
               un_r == 0 and ex_r == 0 and dup_rows == 0 and bad_ck == 0)
    gate.check("%s: %d upstream response rows -> %d responses, 1:1 (unmapped %d, extra %d, doubly mapped %d, seen_ck"
               " differs %d)" % (cv, len(exp_resp) + dup_resp, len(stored_resp), un_x, ex_x, dup_resp, bad_seen),
               un_x == 0 and ex_x == 0 and dup_resp == 0 and bad_seen == 0)
    orphan_v = sum(1 for v in set(stored_rows.values()) | set(stored_resp.values()) if v not in variants)
    orphan_i = sum(1 for i in variants.values() if i not in items)
    gate.check("%s: every source row / response has its variant, every variant its item" % cv, orphan_v == 0 and orphan_i == 0,
               "%d orphan variants, %d orphan items" % (orphan_v, orphan_i))
    n_corpus_items = sum(1 for o in items.values() if o == "corpus")
    for name, got in (("source_rows", len(stored_rows)), ("responses", len(stored_resp)), ("items_corpus", n_corpus_items),
                      ("gpqa_items", gpqa_items)):
        if name in rec:
            gate.check("%s: %s = %d, record %d" % (cv, name, got, rec[name]), got == rec[name],
                       "MATCH" if got == rec[name] else "MISMATCH, reported, not tuned")
    gate.out("  [%s] info %s: items %d (corpus %d, response-only %d), variants %d" % (gate.name, cv, len(items), n_corpus_items,
                                                                                 len(items) - n_corpus_items, len(variants)))


# ── G2 ──────────────────────────────────────────────────────────────────────────────────────

def _load_split(split_path):
    sp = ro.open_ro(split_path, require_sealed=True)
    try:
        meta = dict(sp.execute("SELECT key, value FROM meta"))
        side = {i: (c, s) for i, c, s in sp.execute("SELECT item_id, component_id, side FROM side")}
        comp_side = dict(sp.execute("SELECT component_id, side FROM component"))
    finally:
        sp.close()
    return meta, side, comp_side


def independent_draw(corpus_paths, seed, eval_ratio, gate_ratio):
    """The SECOND implementation of the v2 draw (U, P / O / D, components, strata, draw): data_v2.independent, written
    apart from split.py and passage_closure.py (an AST check in the selftest refuses shared code). Returns
    {item_id: (component_id, side)} over the universe."""
    return independent.draw(corpus_paths, seed, eval_ratio, gate_ratio)[0]


# READY_ck_close_v2 D7: K1 against the SUPERSEDED split (draw 1, b51eb71): the U-excluded items must be exactly the
# author's 840 of the registration, by side TRAIN 523 / EVAL 228 / GATE 89 (docs/judge_v2_program.md L16106). Read from the
# COMMITTED side export of draw 1 (re-hashed from its text and compared with its manifest), so no DB is opened.
SUPERSEDED_DRAW = "REG_ARCHV2-SPLIT-1_c03031568a0a9d827d834b075512b8e4dd095642"
SUPERSEDED_U_SIDES = {"TRAIN": 523, "EVAL": 228, "GATE": 89}


def u_side_counts(excluded, side_of):
    """(counts by side on the superseded split, number of excluded items absent from it)."""
    c = Counter(side_of[i] for i in excluded if i in side_of)
    return dict(c), sum(1 for i in excluded if i not in side_of)


def superseded_u_check(gate, excluded, root=None, expected=None):
    root = root or C.ROOT
    expected = SUPERSEDED_U_SIDES if expected is None else expected
    mdir = os.path.join(root, "data_v2", "manifests")
    tsv = os.path.join(mdir, SUPERSEDED_DRAW + "_side.tsv")
    man = os.path.join(mdir, SUPERSEDED_DRAW + ".json")
    if not (os.path.isfile(tsv) and os.path.isfile(man)):
        gate.check("D7: the superseded split's committed side export and manifest are present (%s)" % SUPERSEDED_DRAW, False)
        return
    # the LF rendering is the rendering of record (CONTEXT rule 8): a checkout under core.autocrlf writes the committed LF
    # export as CRLF, so the text is verified on its LF rendering (a scratch copy) and the working-tree rendering is named
    with open(tsv, "rb") as f:
        raw = f.read()
    lf = raw.replace(b"\r\n", b"\n")
    import tempfile
    fd, tmp_tsv = tempfile.mkstemp(prefix="dv2_superseded_", suffix=".tsv")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(lf)
        try:
            sha, rows = split.verify_side_export(tmp_tsv)
        except SystemExit as e:
            gate.check("D7: the superseded split's side export verifies from its LF text", False, str(e)[:160])
            return
    finally:
        os.remove(tmp_tsv)
    gate.out("  [%s] info D7: superseded side export %s: working tree %s (%d CR bytes); verified on the LF rendering"
             % (gate.name, SUPERSEDED_DRAW[:24], "CRLF" if raw != lf else "LF", raw.count(b"\r")))
    with open(man, "r", encoding="utf-8") as f:
        mpin = json.load(f)["side_export"]["table_sha"]
    gate.check("D7: the superseded split's side export re-hashes from its text to its manifest's table_sha (%s..., %d rows)"
               % (sha[:16], rows), sha == mpin)
    side_of = {}
    for ln in lf.decode("utf-8").split("\n")[2:]:        # the verified LF text, not a re-read of the working tree
        if ln:
            parts = ln.split("\t")
            side_of[parts[0]] = parts[2]
    counts, absent = u_side_counts(excluded, side_of)
    gate.check("D7/K1: the %d U-excluded items sit on the superseded split as %s, %d absent (expected %s, 0 absent)"
               % (len(excluded), json.dumps(counts, sort_keys=True), absent, json.dumps(expected, sort_keys=True)),
               counts == expected and absent == 0)


def _edge_sha_subprocess(corpus_paths, hashseed):
    """K2: the edge-set sha16 computed by split.load_corpora in a FRESH process under PYTHONHASHSEED=hashseed."""
    import subprocess
    env = dict(os.environ, PYTHONHASHSEED=hashseed)
    r = subprocess.run([sys.executable, os.path.abspath(__file__), "--edge-sha"] + list(corpus_paths),
                       capture_output=True, text=True, env=env)
    for ln in r.stdout.splitlines():
        if ln.startswith("EDGE_SHA16 "):
            return ln.split()[1]
    return "FAILED(rc %d: %s)" % (r.returncode, (r.stderr or r.stdout)[-200:])


def _groups(pairs):
    """Connected groups (sorted tuples) of an edge list."""
    parent = {}

    def root(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x
    for a, b in pairs:
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    g = {}
    for a, b in pairs:
        for x in (a, b):
            g.setdefault(root(x), set()).add(x)
    return sorted(tuple(sorted(v)) for v in g.values())


def g2_split(corpus_paths, split_path, gate, hashseed_check=True, superseded=True):
    meta, side, comp_side = _load_split(split_path)
    sp = ro.open_ro(split_path, require_sealed=True)
    try:
        excl = [i for (i,) in sp.execute("SELECT item_id FROM excluded_u ORDER BY item_id")]
        edges = {k: [] for k in "POD"}
        for k, a, b in sp.execute("SELECT kind, item_a, item_b FROM closure_edge ORDER BY kind, item_a, item_b"):
            edges[k].append((a, b))
    finally:
        sp.close()
    # K4: the pinned modules are byte-unchanged (common refuses otherwise; printed here as the witness)
    for name in ("content_closure", "split_side", "passage_closure"):
        blob = ro.git_blob_lf(os.path.join(C.ANALYSIS, name + ".py"))
        gate.check("K4: %s.py blob:%s equals its pin" % (name, blob[:12]), blob == C.PINS[name])
    gate.check("K4: the split was drawn under %s (meta rule %r), normaliser %s" % (split.RULE, meta.get("rule"),
                                                                                meta.get("normaliser")),
               meta.get("rule") == split.RULE and meta.get("normaliser") == C.split_side.NORMALISER_VERSION == "norm-v1")
    idata = independent.read_corpora(corpus_paths)
    icl = independent.closure(idata)
    ind, _ = independent.draw(corpus_paths, meta["seed"], float(meta["eval_ratio"]), float(meta["gate_ratio"]), idata, icl)
    # K1: U, recomputed independently from the corpora
    bad_u = [i for i in excl if idata["v_rows"].get(i) or idata["v_act"].get(i)]
    gate.check("K1: U excludes %d items (digest %s...); 0 of them carry a corpus source_row or an ACTIVE response (%d do);"
               " the independent U excludes the same set" % (len(excl), split.u_digest(excl)[:16], len(bad_u)),
               not bad_u and excl == icl["excluded"] and meta.get("u_digest") == split.u_digest(excl))
    if superseded:
        superseded_u_check(gate, excl)
    gate.check("CK-CLOSE-v2 edges, independent vs sealed: P %d / %d, O %d / %d equal as sets; D %d / %d groups equal"
               % (len(icl["P"]), len(edges["P"]), len(icl["O"]), len(edges["O"]), len(icl["D_groups"]),
                  len(_groups(edges["D"]))),
               icl["P"] == edges["P"] and icl["O"] == edges["O"] and icl["D_groups"] == _groups(edges["D"]))
    d_ind = sum(1 for i, cs in side.items() if ind.get(i) != cs)
    gate.check("the sealed side table agrees item for item with an INDEPENDENT implementation of the v2 draw"
               " (data_v2.independent: U, P / O / D, components, strata, draw; not split.compute) under the seed %r" % meta["seed"],
               d_ind == 0 and set(ind) == set(side), "%d items differ, %d in one only" % (d_ind, len(set(ind) ^ set(side))))
    if hashseed_check:
        shas = [_edge_sha_subprocess(corpus_paths, hs) for hs in ("0", "4242")]
        gate.check("K2: the edge-set sha16 is identical under PYTHONHASHSEED 0 and 4242 (fresh processes) and equals the"
                   " sealed split's: %s / %s / %s" % (shas[0], shas[1], meta.get("edge_set_sha16")),
                   shas[0] == shas[1] == meta.get("edge_set_sha16"))
    data = split.load_corpora(corpus_paths, out=lambda s: None)
    again = split.compute(data, meta["seed"], float(meta["eval_ratio"]), float(meta["gate_ratio"]))
    diff = sum(1 for i, (c, s) in side.items() if again["comp_of"].get(i) != c or again["side_of"].get(c) != s)
    missing = len(set(data["items"]) ^ set(side))
    gate.check("(consistency, NOT independent) the sealed side table equals the builder's own split.compute on the seed %r"
               % meta["seed"], diff == 0 and missing == 0, "%d items differ, %d items not in both" % (diff, missing))
    res = {"comp_of": {i: c for i, (c, _s) in side.items()}, "side_of": comp_side}
    try:
        checks = split.closure_checks(data, res, out=lambda s: gate.out("  " + s))
        ok = checks["moved"] == 0 and checks["families_crossing"] == 0
    except SystemExit as e:
        gate.out("  " + str(e))
        ok = False
    gate.check("CK-CLOSE-v1 on the sealed split through content_closure: moved 0, content-disjoint with the sentinels"
               " explicit, 0 families crossing, no EVAL unit dropped", ok)
    return meta, side


def g2_views(gen_path, eval_path, side, gate):
    g = views.open_generation("construct", gen_path)
    e = views.open_eval("judge", eval_path)
    try:
        keys = C.KeyCache()
        gen_keys = {keys.stem(t) for (t,) in g.execute("SELECT text FROM source_row UNION ALL SELECT stem FROM variant")}
        gen_keys |= {sk for (sk,) in g.execute("SELECT stem_key FROM item")}
        ev_keys = {keys.stem(t) for (t,) in e.execute("SELECT text FROM source_row UNION ALL SELECT stem FROM variant")}
        ev_keys |= {sk for (sk,) in e.execute("SELECT stem_key FROM item")}
        split_ev = {i[2:] for i, (_c, s) in side.items() if s == "EVAL"}
        n_hash = g.execute("SELECT COUNT(*) FROM eval_key_hash").fetchone()[0]
        gen_sides = {s for (s,) in g.execute("SELECT DISTINCT side FROM side")}
        ev_sides = {s for (s,) in e.execute("SELECT DISTINCT side FROM side")}
    finally:
        g.close(); e.close()
    inter = gen_keys & ev_keys
    gate.check("EVAL keys (eval_view) intersect generation keys (gen_view) = %d; gen_view keys %d, eval_view keys %d"
               % (len(inter), len(gen_keys), len(ev_keys)), len(inter) == 0)
    gate.check("gen_view keys intersect the split's EVAL items = %d" % len(gen_keys & split_ev), not (gen_keys & split_ev))
    gate.check("eval_view keys are all EVAL items of the split (%d outside)" % len(ev_keys - split_ev), not (ev_keys - split_ev))
    gate.check("gen_view's salted EVAL hash set has one entry per EVAL item (%d / %d)" % (n_hash, len(split_ev)),
               n_hash == len(split_ev))
    gate.check("side rows: gen_view %s, eval_view %s" % (sorted(gen_sides), sorted(ev_sides)),
               gen_sides <= {"TRAIN", "GATE"} and ev_sides == {"EVAL"})
    item_side = {i: s for i, (_c, s) in side.items()}
    comp_side = {c: s for _i, (c, s) in side.items()}
    for path, opener, stage, admitted in ((gen_path, views.open_generation, "construct", {"TRAIN", "GATE"}),
                                          (eval_path, views.open_eval, "judge", {"EVAL"})):
        conn = opener(stage, path)
        try:
            n, bad = _view_key_coverage(conn, item_side, comp_side, admitted)
        finally:
            conn.close()
        gate.check("%s: EVERY key-bearing column re-keyed (%d values over item ids, stem keys, texts, variant ids,"
                   " source-row ids, component ids, alias targets, representative rows): %d off-side or dangling"
                   % (os.path.basename(path), n, len(bad)), not bad, "; ".join(bad[:3]))


def _view_key_coverage(conn, item_side, comp_side, admitted):
    """READY_archv2_ED D7: every key-bearing column of a view must point to an item on the admitted side, and every id it
    references (variant, source row, component) must resolve inside the view itself. Returns (values checked, problems)."""
    keys = C.KeyCache()
    bad, n = [], 0
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    def item_ok(iid, where):
        nonlocal n
        n += 1
        if item_side.get(iid) not in admitted:
            bad.append("%s: item %s on side %s" % (where, iid[:18], item_side.get(iid)))
    variants = dict(conn.execute("SELECT variant_id, item_id FROM variant"))
    rows = dict(conn.execute("SELECT source_row_id, item_id FROM source_row"))
    for t in sorted(tables):
        cols = [r[1] for r in conn.execute('PRAGMA table_info("%s")' % t)]
        if "item_id" in cols:
            for (iid,) in conn.execute('SELECT item_id FROM "%s"' % t):
                item_ok(iid, t + ".item_id")
    for (sk,) in conn.execute("SELECT stem_key FROM item"):
        item_ok("i:" + sk, "item.stem_key")
    for t, col in (("source_row", "text"), ("variant", "stem")):
        for (txt,) in conn.execute('SELECT "%s" FROM "%s"' % (col, t)):
            item_ok("i:" + keys.stem(txt), "%s.%s re-keyed" % (t, col))
    resp = "response_lite" if "response_lite" in tables else "response"
    for t, col in ((resp, "seen_ck"), ("source_row", "variant_id"), ("reference", "variant_id")):
        for (vid,) in conn.execute('SELECT "%s" FROM "%s"' % (col, t)):
            n += 1
            if vid not in variants:
                bad.append("%s.%s: variant %s not in the view" % (t, col, vid[:18]))
            else:
                item_ok(variants[vid], "%s.%s -> item" % (t, col))
    for kind, tid in conn.execute("SELECT target_kind, target_id FROM alias"):
        n += 1
        m = rows if kind == "source_row" else variants if kind == "variant" else None
        if m is None or tid not in m:
            bad.append("alias target %s %s not in the view" % (kind, tid[:18]))
        else:
            item_ok(m[tid], "alias.target_id -> item")
    for iid, rep in conn.execute("SELECT item_id, representative_row FROM item_subset"):
        n += 1
        if rows.get(rep) != iid:
            bad.append("item_subset.representative_row %s not a row of %s in the view" % (rep[:18], iid[:18]))
    for (js,) in conn.execute("SELECT source_rows_json FROM answer_class"):
        for rid in json.loads(js):
            n += 1
            if rid not in rows:
                bad.append("answer_class source row %s not in the view" % rid[:18])
    for t in ("side", "component"):
        for (cid,) in conn.execute('SELECT component_id FROM "%s"' % t):
            n += 1
            if comp_side.get(cid) not in admitted:
                bad.append("%s.component_id %s on side %s" % (t, cid[:18], comp_side.get(cid)))
    return n, bad


def old_split_control(corpus_conn, listed, gate, record, where):
    """Rebuild an OLD id-split from the corpus_v2 alias rows (namespace legacy_p2dca_engine_id: last row wins, as the
    engine) and count the judgeable ids with a generation-side twin, exact and norm-v1; then run the guard (must refuse)
    and the engine closure (moved)."""
    universe = {}
    for legacy, rid, seq in corpus_conn.execute("SELECT legacy_id, target_id, seq FROM alias WHERE"
                                                " namespace='legacy_p2dca_engine_id' ORDER BY seq"):
        universe[int(legacy)] = rid
    text = dict(corpus_conn.execute("SELECT source_row_id, text FROM source_row"))
    text_of = {q: text[rid] for q, rid in universe.items()}
    listed = set(listed)
    missing = listed - set(universe)
    gate.check("%s: every listed id resolves through the alias rows (%d missing)" % (where, len(missing)), not missing)
    reserved = {q for q in listed if q > 0}
    sentinels = listed - reserved
    gen = set(universe) - listed
    exact_gen = {text_of[q] for q in gen}
    exact = sum(1 for q in reserved if text_of[q] in exact_gen)
    keys = C.KeyCache()
    key_gen = {keys.stem(text_of[q]) for q in gen}
    norm = sum(1 for q in reserved if keys.stem(text_of[q]) in key_gen)
    gate.check("%s: judgeable ids with a generation-side twin, exact text = %d (record %d)" % (where, exact, record["exact"]),
               exact == record["exact"], "MATCH" if exact == record["exact"] else "MISMATCH, reported, not tuned")
    gate.check("%s: judgeable ids with a generation-side twin, norm-v1 = %d (record %d)" % (where, norm, record["norm_v1"]),
               norm == record["norm_v1"], "MATCH" if norm == record["norm_v1"] else "MISMATCH, reported, not tuned")
    try:
        C.cc.assert_content_disjoint(gen, reserved, sentinels, text_of, where=where + " (the old split; must REFUSE)",
                                     out=lambda s: gate.out("    " + s))
        refused = None
    except C.cc.ContentLeak as e:
        refused = e.counts
    gate.check("%s: the guard REFUSES the old split (not vacuous)" % where, refused is not None,
               "refusal counts %s" % (json.dumps(refused, sort_keys=True) if refused else "none"))
    r = C.cc.closed_complement(gen, reserved, sentinels, text_of)
    mv = r["counts"]["n_moved"]
    gate.check("%s: content_closure moves %d generation-side rows (record %d)" % (where, mv, record["moved"]),
               mv == record["moved"], "by reason %s" % json.dumps({k: v for k, v in r["counts"]["by_reason"].items() if v}))


def _pool_guard():
    path = os.path.join(C.ANALYSIS, "pool_guard.py")
    blob = ro.git_blob_lf(path)
    pin = "6521b51ac0fce04063563f9e6dcf42554ad86591"
    if blob != pin:
        C._refuse("pool_guard.py blob:%s is not the pinned blob:%s" % (blob, pin))
    return C.cc._load_sibling("pool_guard")


def g2_p2dca_control(mmlu_corpus_path, gate):
    pg = _pool_guard()
    with open(P2DCA_ID_FILE, "r", encoding="utf-8") as f:
        ids = json.load(f)
    pid = pg.compute_pool_id(pg.judgeable(ids))
    gate.check("the id file %s re-hashes to %s" % (os.path.relpath(P2DCA_ID_FILE, C.ROOT).replace("\\", "/"), pid), pid == P2DCA)
    listed = [q for v in ids.values() for q in v]
    gate.out("  [%s] info p2dca: %d listed ids (%d judgeable, %d sentinels)" % (gate.name, len(listed),
                                                                           sum(1 for q in listed if q > 0),
                                                                           sum(1 for q in listed if q <= 0)))
    c = ro.open_ro(mmlu_corpus_path, require_sealed=True)
    try:
        old_split_control(c, listed, gate, P2DCA_RECORD, "OLD p2dca split")
    finally:
        c.close()


# ── G4 ──────────────────────────────────────────────────────────────────────────────────────

def _refused(fn, *a, **k):
    try:
        conn = fn(*a, **k)
    except SystemExit as e:
        return True, str(e)
    conn.close()
    return False, "admitted"


def g4_loaders(gen_path, eval_path, gate):
    for stage in views.GENERATION_STAGES:
        r, msg = _refused(views.open_generation, stage, gen_path)
        gate.check("open_generation(%r) on gen_view is ADMITTED" % stage, not r, msg[:90])
        r, msg = _refused(views.open_eval, stage, eval_path)
        gate.check("open_eval(%r) on eval_view is REFUSED" % stage, r, msg[:110])
    for stage in views.EVAL_STAGES:
        r, msg = _refused(views.open_eval, stage, eval_path)
        gate.check("open_eval(%r) on eval_view is ADMITTED" % stage, not r, msg[:90])
        r, msg = _refused(views.open_generation, stage, gen_path)
        gate.check("open_generation(%r) on gen_view is REFUSED" % stage, r, msg[:110])
    r, msg = _refused(views.open_generation, "construct", eval_path)
    gate.check("open_generation('construct') handed the EVAL file is REFUSED by the file's own meta", r, msg[:120])
    r, msg = _refused(views.open_eval, "route", gen_path)
    gate.check("open_eval('route') handed the GEN file is REFUSED by the file's own meta", r, msg[:120])
    for fn in (views.open_generation, views.open_eval):
        r, msg = _refused(fn, "rubric_writer", gen_path)
        gate.check("%s('rubric_writer') (an unknown stage) is REFUSED" % fn.__name__, r, msg[:100])
    r, msg = _refused(views.open_generation, "construct", gen_path, expect_sha256="0" * 64)
    gate.check("open_generation with a wrong pinned sha256 is REFUSED", r, msg[:100])
    g = views.open_generation("label", gen_path)
    e = views.open_eval("arena", eval_path)
    try:
        ev_text = e.execute("SELECT text FROM source_row ORDER BY source_row_id LIMIT 1").fetchone()[0]
        tr_text = g.execute("SELECT text FROM source_row ORDER BY source_row_id LIMIT 1").fetchone()[0]
        try:
            views.assert_not_eval(g, [tr_text, ev_text], where="G4 probe")
            refused = False
        except SystemExit:
            refused = True
        gate.check("assert_not_eval refuses a generation artefact carrying an EVAL text", refused)
        gate.check("assert_not_eval admits a TRAIN/GATE text", views.assert_not_eval(g, [tr_text], where="G4 probe") == 0)
    finally:
        g.close(); e.close()


# ── G5 ──────────────────────────────────────────────────────────────────────────────────────

def _meta(run_id):
    return {"run_id": run_id, "registration": "G5-SELFTEST (no registration: a scratch store)", "judge_requested": "none",
            "provider": "none", "max_tokens": 8192, "temperature_label": "omitted", "script_blob": "0" * 40,
            "combiner_blob": "0" * 40, "prompt_template_blob": "0" * 40, "parse_version": "none", "pool_id": "pv2dev_selftest"}


def _slot(match, order, draw, a="mA", b="mB"):
    first, second = (a, b) if order == 1 else (b, a)
    return {"match_id": match, "presentation_order": order, "draw_index": draw, "variant_id": "v:x", "stem_key": "k",
            "component_id": "c:k", "contestant_a": a, "contestant_b": b, "shown_first": first, "shown_second": second,
            "response_first_sha": "r1", "response_second_sha": "r2"}


def _fields(vote, **kw):
    f = {"vote": vote, "raw_text": None if vote == "CONTENT_FILTER" else "raw", "parse_version": "none",
         "judge_requested": "none", "provider": "none", "max_tokens": 8192, "temperature_sent": None,
         "temperature_label": "omitted", "prompt_template_blob": "0" * 40, "script_blob": "0" * 40,
         "combiner_blob": "0" * 40, "stem_key": "k", "pool_id": "pv2dev_selftest", "http_status": 200,
         "finish_reason": "length" if vote == "NON_TERMINATED" else "stop"}
    f.update(kw)
    return f


def _abort_msg(conn, sql, args=()):
    """None when the statement is admitted (and committed); the error text when SQLite refuses it (rolled back)."""
    try:
        conn.execute(sql, args)
        conn.commit()
        return None
    except sqlite3.DatabaseError as e:
        conn.rollback()
        return str(e)


def _mutation_fails(conn, sql, args=()):
    try:
        conn.execute(sql, args)
        conn.commit()
        return False
    except sqlite3.DatabaseError:
        conn.rollback()
        return True


def g5_append_only(gate, tmpdir):
    import hashlib
    path = os.path.join(tmpdir, "g5_run.db")
    st = verdicts.VerdictStore.create(path, _meta("g5"))
    slots = [_slot("m1", 1, 0), _slot("m1", 2, 0), _slot("m2", 1, 0), _slot("m2", 2, 0),
             _slot("m1", 1, 1), _slot("m1", 2, 1)]
    st.add_schedule(slots)
    body = b'{"same": "body"}'
    sha = hashlib.sha256(body).hexdigest()
    script = {("m1", 1, 0): ("verdict", body, sha, _fields("FIRST")),
              ("m1", 2, 0): ("verdict", body, sha, _fields("SECOND")),
              ("m2", 1, 0): ("verdict", b"cf", hashlib.sha256(b"cf").hexdigest(), _fields("CONTENT_FILTER", http_status=400)),
              ("m2", 2, 0): ("error", hashlib.sha256(b"e").hexdigest(), 503, "http_503"),
              ("m1", 1, 1): ("verdict", body, sha, _fields("FIRST")),
              ("m1", 2, 1): ("verdict", body, sha, _fields("NON_TERMINATED"))}
    posted = []

    def poster(slot):
        k = (slot["match_id"], slot["presentation_order"], slot["draw_index"])
        posted.append(k)
        return script[k]
    n1 = st.drain(poster)
    gate.check("first launch posts every scheduled slot (%d of %d)" % (n1, len(slots)), n1 == len(slots))
    n_same = st.conn.execute("SELECT COUNT(*) FROM verdict WHERE payload_sha256=?", (sha,)).fetchone()[0]
    gate.check("R7: one payload body posted in two draws and two orders is stored %d times (the key is the slot)" % n_same,
               n_same == 4)
    c = st.conn
    for t in verdicts.TABLES:
        if t == ro.SEAL_TABLE:
            continue
        gate.check("UPDATE on %s aborts" % t, _mutation_fails(c, "UPDATE %s SET run_id = run_id" % t if t != "run_meta"
                                                               else "UPDATE run_meta SET value = value"))
        gate.check("DELETE on %s aborts" % t, _mutation_fails(c, "DELETE FROM %s" % t))
    # D5: INSERT OR REPLACE on an existing key must ABORT and leave the row as it was (REPLACE does not fire DELETE triggers)
    before_v = c.execute("SELECT vote, raw_text FROM verdict WHERE match_id='m1' AND presentation_order=1 AND draw_index=0").fetchone()
    before_m = c.execute("SELECT value FROM run_meta WHERE key='registration'").fetchone()
    probes = (
        ("verdict", "INSERT OR REPLACE INTO verdict (run_id, match_id, presentation_order, draw_index, vote, raw_text,"
                    " parse_version, payload_sha256, body_zlib, body_codec, judge_requested, provider, max_tokens,"
                    " temperature_label, content_filter, n_attempts, prompt_template_blob, script_blob, combiner_blob,"
                    " stem_key, pool_id, created_at) VALUES ('g5','m1',1,0,'SECOND','FORGED','p','s',x'00','zlib','j','p',"
                    "8192,'omitted',0,1,'b','b','b','k','p','t')"),
        ("run_meta", "INSERT OR REPLACE INTO run_meta (key, value) VALUES ('registration', 'FORGED')"),
        ("run_meta (REPLACE INTO)", "REPLACE INTO run_meta (key, value) VALUES ('registration', 'FORGED')"),
        ("attempt", "INSERT OR REPLACE INTO attempt VALUES ('g5','m1',1,0,1,200,NULL,NULL,'forged','t')"),
        ("verdict (OR IGNORE)", "INSERT OR IGNORE INTO verdict (run_id, match_id, presentation_order, draw_index, vote,"
                                " raw_text, parse_version, payload_sha256, body_zlib, body_codec, judge_requested, provider,"
                                " max_tokens, temperature_label, content_filter, n_attempts, prompt_template_blob,"
                                " script_blob, combiner_blob, stem_key, pool_id, created_at) VALUES ('g5','m1',1,0,'TIE','x',"
                                "'p','s',x'00','zlib','j','p',8192,'omitted',0,1,'b','b','b','k','p','t')"))
    for t, sql in probes:
        msg = _abort_msg(c, sql)
        gate.check("INSERT OR REPLACE / REPLACE / OR IGNORE on an existing %s key ABORTS by the no-rekey trigger" % t,
                   msg is not None and "key already present" in msg, msg or "ADMITTED")
    gate.check("... and the rows are unchanged (verdict %s, run_meta registration %r)" % (before_v, before_m[0]),
               c.execute("SELECT vote, raw_text FROM verdict WHERE match_id='m1' AND presentation_order=1 AND draw_index=0"
                         ).fetchone() == before_v
               and c.execute("SELECT value FROM run_meta WHERE key='registration'").fetchone() == before_m)
    gate.check("a schedule insert after the first call aborts",
               _mutation_fails(c, "INSERT INTO schedule (run_id, match_id, presentation_order, draw_index, variant_id,"
                                  " stem_key, contestant_a, contestant_b, shown_first, shown_second, response_first_sha,"
                                  " response_second_sha) VALUES ('g5','m9',1,0,'v','k','a','b','a','b','x','y')"))
    gate.check("a verdict for a slot not in the schedule aborts",
               _mutation_fails(c, "INSERT INTO verdict (run_id, match_id, presentation_order, draw_index, vote, raw_text,"
                                  " parse_version, payload_sha256, body_zlib, body_codec, judge_requested, provider,"
                                  " max_tokens, temperature_label, content_filter, n_attempts, prompt_template_blob,"
                                  " script_blob, combiner_blob, stem_key, pool_id, created_at) VALUES ('g5','m9',1,0,"
                                  "'TIE','r','p','s',x'00','zlib','j','p',1,'omitted',0,1,'b','b','b','k','p','t')"))
    for bad, why in ((dict(vote="TIE", finish_reason="length"), "a truncated call stored as TIE"),
                     (dict(vote="NON_TERMINATED", finish_reason="stop"), "NON_TERMINATED without finish_reason length"),
                     (dict(vote="TIE", temperature_sent=0.0), "a temperature sent while labelled omitted")):
        try:
            f = _fields(bad["vote"])
            f.update(bad)
            st.record_verdict(("g5", "m2", 2, 0), body, sha, **f)
            ok = False
        except (sqlite3.DatabaseError, SystemExit):
            c.rollback()
            ok = True
        gate.check("the CHECKs refuse %s" % why, ok)
    try:
        st.record_verdict(("g5", "m2", 2, 0), body, "0" * 64, **_fields("TIE"))
        ok = False
    except SystemExit:
        ok = True
    gate.check("a payload_sha256 that is not sha256(body) is refused", ok)
    try:
        st.record_verdict(("g5", "m2", 2, 0), body, sha, **_fields("LEFT"))
        ok = False
    except SystemExit:
        ok = True
    gate.check("a vote outside the six-way enum is refused (LEFT)", ok)
    for bad, why in (({"stem_key": "another-key"}, "a stem_key that differs from the schedule slot"),
                     ({"reference_row_id": "ref-9"}, "a reference_row_id the schedule slot does not carry"),
                     ({"reference_vintage": "v9"}, "a reference_vintage the schedule slot does not carry")):
        f = _fields("TIE")
        f.update(bad)
        try:
            st.record_verdict(("g5", "m2", 2, 0), body, sha, **f)
            ok = False
        except sqlite3.DatabaseError as e:
            c.rollback()
            ok = "differ from the schedule slot" in str(e)
        gate.check("the verdict_equals_schedule trigger refuses %s" % why, ok)
    ms = {(m, d): comb for m, d, comb in c.execute("SELECT match_id, draw_index, combined FROM match_status")}
    n_sched = c.execute("SELECT COUNT(*) FROM (SELECT DISTINCT run_id, match_id, draw_index FROM schedule)").fetchone()[0]
    n_inner = c.execute("SELECT COUNT(*) FROM match_verdict").fetchone()[0]
    gate.check("denominators: match_status lists all %d scheduled matches (m2/0 %s while its order 2 errored); the inner"
               " join match_verdict has %d" % (n_sched, ms.get(("m2", 0)), n_inner),
               len(ms) == n_sched == 3 and ms.get(("m2", 0)) == "PENDING" and n_inner == 2)
    st.conn.close()
    st2 = verdicts.VerdictStore.open(path)
    pend = [tuple(r[1:4]) for r in st2.pending()]
    gate.check("relaunch anti-join: pending = the errored slot only %s (the cached CONTENT_FILTER is not pending)" % pend,
               pend == [("m2", 2, 0)])
    posted.clear()
    script[("m2", 2, 0)] = ("verdict", body, sha, _fields("TIE"))
    n2 = st2.drain(poster)
    gate.check("the relaunch posts exactly the pending slot (%d post: %s)" % (n2, posted), n2 == 1 and posted == [("m2", 2, 0)])
    n_att = st2.conn.execute("SELECT n_attempts FROM verdict WHERE match_id='m2' AND presentation_order=2").fetchone()[0]
    gate.check("the relaunch's verdict counts both attempts (n_attempts %d)" % n_att, n_att == 2)
    posted.clear()
    n3 = st2.drain(poster)
    gate.check("a COMPLETED run's relaunch posts NOTHING (%d posts)" % n3, n3 == 0 and posted == [])
    mv = {(m, d): comb for m, d, comb in st2.conn.execute("SELECT match_id, draw_index, combined FROM match_verdict")}
    gate.check("match_verdict: FIRST/SECOND over the two orders is A twice -> A; CONTENT_FILTER propagates; NON_TERMINATED"
               " propagates %s" % json.dumps({"%s/%d" % k: v for k, v in sorted(mv.items())}),
               mv.get(("m1", 0)) == "A" and mv.get(("m2", 0)) == "CONTENT_FILTER" and mv.get(("m1", 1)) == "NON_TERMINATED")
    sealed = st2.seal()
    gate.check("seal: the run DB is sealed and read-only (sha256-bytes %s)" % sealed["sha256_bytes"][:16],
               not os.access(path, os.W_OK))
    try:
        verdicts.VerdictStore.open(path)
        ok = False
    except SystemExit:
        ok = True
    gate.check("a sealed run refuses a writer", ok)
    try:
        ro.open_run_writer(os.path.join(tmpdir, "g5_missing.db"))
        ok = False
    except SystemExit:
        ok = True
    gate.check("open_run_writer refuses a missing file", ok)
    c2 = ro.create_new(os.path.join(tmpdir, "record_like.db"))
    c2.execute("CREATE TABLE t (x)"); c2.commit(); c2.close()
    try:
        ro.open_run_writer(os.path.join(tmpdir, "record_like.db"))
        ok = False
    except SystemExit:
        ok = True
    gate.check("open_run_writer refuses a DB that is not a v2 verdict DB (read-only probe first)", ok)
    try:
        ro.create_new(path)
        ok = False
    except SystemExit:
        ok = True
    gate.check("create_new refuses an existing path (write-once)", ok)


# ── the real run ────────────────────────────────────────────────────────────────────────────

def run_build_dir(build_dir, out=print, data_root=None):
    data_root = data_root or C.DATA_ROOT
    corp = sorted(glob.glob(os.path.join(build_dir, "corpus_v2_*.db")))
    sp = glob.glob(os.path.join(build_dir, "split_v2_*.db"))
    gv = glob.glob(os.path.join(build_dir, "gen_view_*.db"))
    ev = glob.glob(os.path.join(build_dir, "eval_view_*.db"))
    if len(corp) < 1 or len(sp) != 1 or len(gv) != 1 or len(ev) != 1:
        C._refuse("%s does not hold one split, one gen_view, one eval_view and the corpora" % build_dir)
    out("[GATES] build %s; data root %s (read-only); content_closure blob:%s; split_side blob:%s"
        % (build_dir, data_root, C.PINS["content_closure"], C.PINS["split_side"]))
    fails = []
    for name, fn in (("G1", lambda g: [g1_corpus(p, data_root, g) for p in corp]),
                     ("G2", lambda g: (g2_views(gv[0], ev[0], g2_split(corp, sp[0], g)[1], g),
                                       g2_p2dca_control([p for p in corp if "mmlu_pro" in p][0], g))),
                     ("G4", lambda g: g4_loaders(gv[0], ev[0], g))):
        g = Gate(name, out)
        out("[GATE %s]" % name)
        fn(g)
        try:
            g.close()
        except SystemExit:
            fails.append(name)
    g = Gate("G5", out)
    out("[GATE G5] (a NEW scratch verdict DB in a temporary directory)")
    tmp = tempfile.mkdtemp(prefix="dv2_g5_")
    try:
        g5_append_only(g, tmp)
    finally:
        _rmtree(tmp)
    try:
        g.close()
    except SystemExit:
        fails.append("G5")
    out("[GATES] %s" % ("ALL PASS (G1 G2 G4 G5)" if not fails else "FAILED: %s" % ", ".join(fails)))
    if fails:
        raise SystemExit(1)
    return 0


def _rmtree(p):
    """Best-effort removal of a temporary directory (sealed files are read-only; a handle still open after a failure
    must not mask the failure itself)."""
    def onerr(fn, path, _exc):
        try:
            os.chmod(path, 0o666)
            fn(path)
        except OSError:
            pass
    shutil.rmtree(p, onerror=onerr)


# ── selftest: a synthetic end-to-end build (no DB of record is opened) ─────────────────────

def _fixture(root):
    """Two tiny source DBs with the schemas of record, written as NEW files in a temporary data root."""
    m = ro.create_new(os.path.join(root, "mmlu_pro_dataset_cache_v2.db"))
    m.executescript("""
      CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT);
      CREATE TABLE eval_results (question_id INTEGER NOT NULL, model_name TEXT NOT NULL, category TEXT NOT NULL,
        question_text TEXT NOT NULL, options_json TEXT NOT NULL, gt_answer TEXT NOT NULL, pred TEXT, model_output TEXT NOT NULL,
        is_correct INTEGER NOT NULL DEFAULT 0, is_reserved INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (question_id, model_name));
      CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT NOT NULL,
        has_embedding INTEGER NOT NULL DEFAULT 0);
      CREATE TABLE ag_news (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, options TEXT, answer TEXT);
    """)
    qs = []
    for i in range(1, 61):
        cat = "math" if i % 2 else "law"
        qs.append(("Question number %d about %s?" % (i, cat), cat, json.dumps(["w%d" % i, "x%d" % i, "y%d" % i]), "B"))
    qs.append(("Question number 1 about math?", "math", json.dumps(["y1", "w1", "x1"]), "C"))   # shuffled twin of row 1
    qs.append(("QUESTION   number 2 about law?", "law", json.dumps(["other", "set"]), "A"))     # norm-v1 twin of row 2
    qs.append(("Question number 3 about math?", "math", json.dumps(["p", "q"]), "A"))          # exact-text twin of row 3
    # CK-CLOSE-v2 K3 fixtures (rows 64-85, corpus rows without responses; words unique per case, so runs are exact)
    for text, opts in K3_MMLU_ROWS:
        qs.append((text, "math", json.dumps(opts), "A"))
    for q in qs:
        m.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?,?,?,?,?)",
                  (q[0], q[1], "", q[2], q[3]))
    m.execute("INSERT INTO ag_news (question, category) VALUES ('foreign row', 'World')")
    models = ["mA", "mB", "Meta-Llama-3-70B-Instruct"]
    for rid in range(1, 61):
        qid = 100 + rid
        m.execute("INSERT INTO eval_question_link VALUES (?,?,?,0)", (qid, rid, qs[rid - 1][0]))
        for mo in models:
            q = qs[rid - 1]
            if mo == "Meta-Llama-3-70B-Instruct":
                q = qs[rid % 60]                                   # id-shifted, as the record's Llama rows
            opts = q[2] if not (mo == "mB" and rid == 5) else json.dumps(list(reversed(json.loads(q[2]))))
            text = q[0] if not (mo == "mB" and rid == 7) else q[0] + " (reworded)"   # a qid with two stems
            m.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
                      (qid, mo, q[1], text, opts, q[3], "B", "out %s %d" % (mo, rid), int(mo == "mA")))
        if rid <= 30 and rid != 7:                                 # the legacy solver's row (none for the 2-stem qid)
            q = qs[rid - 1]
            # qid 120: the solver saw its OWN rendering (a minority variant among the active rows): the reference must
            # follow the solver, not the modal active variant (READY_archv2_ED D6, mutant M5c)
            stext = q[0] + " (solver rendering)" if rid == 20 else q[0]
            m.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,1)",
                      (qid, ingest.SOLVER_MODEL, q[1], stext, q[2], q[3], "B", "solver-row %d" % rid, 1))
    # CK-CLOSE-v2 U (K1): a question only the QUARANTINED model ever answered, with a text no corpus row carries
    m.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
              (200, "Meta-Llama-3-70B-Instruct", "math", K3_QUARANTINED_ONLY, json.dumps(["x", "y"]), "A", "A", "q-only", 1))
    m.commit(); m.close()
    js = os.path.join(root, "experiment_results", "judge_solve")
    os.makedirs(js)
    r0 = ro.create_new(os.path.join(js, "grok-reasoning.db"))
    r0.execute("CREATE TABLE answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT,"
               " tokens INTEGER, latency REAL, ts REAL)")
    for q in range(101, 141):
        r0.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?)", (q, "B", "B", 1, "solve %d" % q, 10, 1.0, 1757400000.0))
    r0.commit(); r0.close()
    r1 = ro.create_new(os.path.join(js, "grok-reasoning-v1.db"))
    r1.execute("CREATE TABLE answers (question_id INTEGER PRIMARY KEY, answer TEXT, gt TEXT, correct INTEGER, raw TEXT,"
               " tokens INTEGER, latency REAL, ts REAL, state TEXT, response_id TEXT, reference_model TEXT, protocol_id TEXT,"
               " max_tokens INTEGER, temperature TEXT, finish_reason TEXT, completion_tokens INTEGER, minted_at TEXT,"
               " side_at_mint TEXT)")
    for q in range(101, 106):
        r1.execute("INSERT INTO answers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (q, "B", "B", 1, "v1 %d" % q, 10, 1.0, 1758200000.0, "YIELD", "resp-%d" % q, "grok", "solve_json_v1",
                    4096, "omitted", "stop", 10, "2026-09-19T00:00:00Z", "EVAL(copied)"))
    r1.commit(); r1.close()
    u = ro.create_new(os.path.join(root, "multicorpus_cache_v1.db"))
    u.executescript("""
      CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT NOT NULL, upstream_id INTEGER NOT NULL, task TEXT NOT NULL,
        domain TEXT NOT NULL, text TEXT NOT NULL, options_json TEXT, target TEXT, verifier TEXT NOT NULL, generative INTEGER NOT NULL);
      CREATE TABLE eval_results (question_id INTEGER NOT NULL, model_name TEXT NOT NULL, category TEXT NOT NULL, question_text TEXT NOT NULL,
        options_json TEXT, gt_answer TEXT, pred TEXT, model_output TEXT NOT NULL, is_correct INTEGER NOT NULL DEFAULT 0, is_reserved INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (question_id, model_name));
      CREATE TABLE eval_results_mathfix (question_id INTEGER, model_name TEXT, is_correct INTEGER, PRIMARY KEY (question_id, model_name));
    """)
    rows = [(101, "MMLU_PRO", 101, "mmlu_pro_math", "math", qs[0][0], qs[0][2], "B", "MC_LETTER", 0)]  # cross-corpus twin
    for k in range(20):
        rows.append((5000000 + k, "GPQA", k, "gpqa_diamond", "Physics", "GPQA stem %d" % k, json.dumps(["a%d" % k, "b%d" % k]), "(A)",
                     "IMPORTED:acc_norm", 0))
        rows.append((5000100 + k, "GPQA", 100 + k, "gpqa_main", "Physics", "GPQA stem %d" % k, json.dumps(["b%d" % k, "a%d" % k]), "(B)",
                     "IMPORTED:acc_norm", 0))
    # 40 BBH items in ONE task, so the 5% mask is 2 items: k 30-31 share a 20-token run (held by 2: unmasked, joined);
    # k 32-34 share one (held by 3 > 2: masked by the BBH rule, although df 3 <= R would unmask it)
    for k in range(40):
        harness = [repr({"arg_0": "<|user|>Q: expr %d" % k, "arg_1": v}) for v in ("True", "False")]
        rows.append((1000000 + k, "BBH", k, "bbh_bool", "boolean", K3_BBH_STEMS.get(k, "expr %d is" % k), json.dumps(harness),
                     "False", "IMPORTED:acc_norm", 0))
    for k in range(30):
        harness = [repr({"arg_0": "<|user|>Q: lie %d" % k, "arg_1": v}) for v in ("Yes", "No")]
        rows.append((1000100 + k, "BBH", 100 + k, "bbh_web", "web_of_lies", K3_BBH2_STEMS.get(k, "lie %d is" % k),
                     json.dumps(harness), "No", "IMPORTED:acc_norm", 0))
    for k in range(20):
        rows.append((2000000 + k, "MATH", k, "math_algebra", "Algebra", "Solve %d x = 1" % k, None, "1/%d" % (k + 1),
                     "IMPORTED:exact_match", 1))
    # a 5-component stratum: 0.30 * 5 = 1.5 and 0.10 * 5 = 0.5, so round-half-up and floor differ (READY_archv2_ED D2,
    # mutant M15); the other fixture strata have integral shares
    for k in range(5):
        rows.append((3000000 + k, "MUSR", k, "musr_murder_mysteries", "murder_mysteries", "Who did it, case %d?" % k,
                     json.dumps(["Ann", "Bob"]), "Ann", "IMPORTED:acc_norm", 0))
    for r in rows:
        u.execute("INSERT INTO corpus_questions VALUES (?,?,?,?,?,?,?,?,?,?)", r)
    for r in rows:
        for mo in ("uA", "uB"):
            oj = r[6]
            if r[1] == "BBH" and mo == "uB":
                oj = json.dumps([repr({"arg_0": "<s>[INST] Q: expr [/INST]", "arg_1": v}) for v in ("True", "False")])
            u.execute("INSERT INTO eval_results VALUES (?,?,?,?,?,?,?,?,?,0)",
                      (r[0], mo, r[4], r[5], oj, r[7], "x", "o", 1))
            if r[1] == "MATH":
                u.execute("INSERT INTO eval_results_mathfix VALUES (?,?,?)", (r[0], mo, 0))
    u.commit(); u.close()
    repo = os.path.join(os.path.dirname(root), "repo")
    os.makedirs(os.path.join(repo, "experiment_configs"))
    with open(os.path.join(repo, "experiment_configs", "reserved_pool_frozen_p2dca.json"), "w", encoding="utf-8") as f:
        json.dump({"math": list(range(101, 119)), "law": [-1000061]}, f)
    n_k3_items = len({C.split_side.stem_key(t) for t, _o in K3_MMLU_ROWS})   # the two-variant item counts once
    return {"mmlu-pro-v2": {"source_rows": len(qs), "items_corpus": 60 + n_k3_items, "responses": 210},
            "mc6-2026-09-11": {"source_rows": len(rows), "items_corpus": 116, "gpqa_items": 20, "responses": 2 * len(rows)}}


def selftest(out=print):
    tmp = tempfile.mkdtemp(prefix="dv2_selftest_")
    total = {"checks": 0}

    def say(s):
        if "] PASS " in s or "] FAIL " in s:
            total["checks"] += 1
        out(s)
    try:
        data_root = os.path.join(tmp, "data"); os.mkdir(data_root)
        build = os.path.join(tmp, "build"); os.mkdir(build)
        rec = _fixture(data_root)
        quiet = lambda s: None
        paths = [ingest.build_corpus(cv, build, out=quiet, data_root=data_root, repo_root=os.path.join(tmp, "repo"))["path"]
                 for cv in ("mmlu-pro-v2", "mc6-2026-09-11")]
        sp = split.build_split(paths, build, "DEV-selftest", out=quiet)
        gv = views.build_view("gen", paths, sp["path"], build, out=quiet)
        ev = views.build_view("eval", paths, sp["path"], build, out=quiet)
        g = Gate("SELFTEST-G1", say)
        for p in paths:
            cv = _one(p, "SELECT value FROM meta WHERE key='corpus_version'")
            g1_corpus(p, data_root, g, record=rec[cv])
        g.close()
        # G1 negative control: a source DB with one more row must FAIL the bijection
        neg = os.path.join(tmp, "neg"); os.mkdir(neg)
        shutil.copy(os.path.join(data_root, "mmlu_pro_dataset_cache_v2.db"), neg)
        shutil.copytree(os.path.join(data_root, "experiment_results"), os.path.join(neg, "experiment_results"))
        cw = ro.open_scratch_rw(os.path.join(neg, "mmlu_pro_dataset_cache_v2.db"))
        cw.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES ('an extra row?','law','','[\"a\"]','A')")
        cw.commit(); cw.close()
        gn = Gate("SELFTEST-G1-NEG", lambda s: None)
        g1_corpus(paths[0], neg, gn, record=rec["mmlu-pro-v2"])
        g = Gate("SELFTEST-G1neg", say)
        g.check("G1 FAILS on a source with one extra upstream row (%d failing checks: %s)" % (len(gn.fails), "; ".join(gn.fails)[:160]),
                len(gn.fails) >= 2)
        g.close()
        g = Gate("SELFTEST-G2", say)
        meta, side = g2_split(paths, sp["path"], g, superseded=False)   # D7 runs on real builds; its counting is tested below
        g2_views(gv["path"], ev["path"], side, g)
        # the shuffled twin (row 61) and the norm-v1 twin (row 62) sit with their partners; the cross-corpus MMLU_PRO row
        # of the union is the SAME item as mmlu_pro row 1; the reworded qid 107 is one component with its stem
        g.check("a shuffled twin collapses to one variant", _one(paths[0], "SELECT COUNT(DISTINCT variant_id) FROM source_row"
                                                               " WHERE upstream_pk IN (1, 61)") == 1)
        g.check("a norm-v1 twin is one item, two variants",
                _one(paths[0], "SELECT COUNT(DISTINCT item_id) FROM source_row WHERE upstream_pk IN (2, 62)") == 1 and
                _one(paths[0], "SELECT COUNT(DISTINCT variant_id) FROM source_row WHERE upstream_pk IN (2, 62)") == 2)
        g.check("BBH harness pairs rendered in two chat templates key to ONE variant (opt-v1)",
                _one(paths[1], "SELECT COUNT(DISTINCT seen_ck) FROM response WHERE legacy_qid = 1000003") == 1)
        g.check("GPQA diamond + main copies collapse to one item with two subset tags (20 items)",
                _one(paths[1], "SELECT COUNT(DISTINCT item_id) FROM item_subset") == 20 and
                _one(paths[1], "SELECT COUNT(*) FROM item_subset") == 40)
        sp_c = ro.open_ro(sp["path"], require_sealed=True)
        try:
            comps = dict(sp_c.execute("SELECT item_id, component_id FROM side"))
        finally:
            sp_c.close()
        k107 = [r[0] for r in _all(paths[0], "SELECT DISTINCT item_id FROM response WHERE legacy_qid = 107"
                                             " AND model != 'Meta-Llama-3-70B-Instruct'")]
        g.check("a legacy qid whose active rows carry two stems is ONE component (%d items -> %d component)"
                % (len(k107), len({comps[i] for i in k107})), len(k107) == 2 and len({comps[i] for i in k107}) == 1)
        g.check("the quarantined model's id-shifted rows add no family edge (Llama rows keyed by their own text)",
                _one(paths[0], "SELECT n_content_mismatch FROM quarantine_check") == 60)
        # negative control 1: a legacy-qid family split across the EVAL boundary must be REFUSED
        data = split.load_corpora(paths, out=quiet)
        res = split.compute(data, "DEV-selftest")
        k107_items = sorted(k107)
        tampered = {"comp_of": dict(res["comp_of"]), "side_of": dict(res["side_of"])}
        tampered["comp_of"][k107_items[0]] = "c:tamper"
        tampered["side_of"]["c:tamper"] = "EVAL" if res["side_of"][res["comp_of"][k107_items[1]]] != "EVAL" else "TRAIN"
        try:
            split.closure_checks(data, tampered, out=quiet)
            refused = False
        except SystemExit as e:
            refused = "cross the EVAL boundary" in str(e)
        g.check("closure_checks REFUSES a split where a legacy-qid family straddles the EVAL boundary", refused)
        # negative control 2: one stem_key on both sides (a unit re-assigned to a fresh item on the other side) must be
        # REFUSED by content_closure (build_closure moves it)
        try:
            split.closure_checks(data, _straddle(data, res), out=quiet)
            refused = False
        except SystemExit as e:
            refused = "not closed" in str(e) or "[CK-CLOSE]" in str(e)
        g.check("closure_checks REFUSES a split where two units of one stem_key straddle the sides (content_closure)", refused)
        # the positive control on an OLD id split rebuilt from the alias rows (the engine universe: rows 1..60 carry eval
        # qids 101..160, rows 61..63 are unlinked, -1000061..-1000063): listed = qids 101..118 (judgeable) + -1000061
        # (a sentinel, the shuffled twin of row 1). Generation side = rows 19..60 + rows 62, 63. Row 3 has the exact-text
        # twin row 63; row 2 has the norm-v1-only twin row 62: exact 1, norm-v1 2, moved 2 (rows 62, 63).
        c = ro.open_ro(paths[0], require_sealed=True)
        try:
            listed = list(range(101, 119)) + [-1000061]
            old_split_control(c, listed, g, {"exact": 1, "norm_v1": 2, "moved": 2}, "SYNTHETIC old split")
        finally:
            c.close()
        g.close()
        g = Gate("SELFTEST-5618b78-FIXES", say)
        # (1) verbatim ordered options per response: qid 105's mB row has its options REVERSED (same variant)
        c = ro.open_ro(paths[0], require_sealed=True)
        try:
            oa, ck_a = c.execute("SELECT options_ordered_sha, seen_ck FROM response WHERE legacy_qid=105 AND model='mA'").fetchone()
            ob, ck_b = c.execute("SELECT options_ordered_sha, seen_ck FROM response WHERE legacy_qid=105 AND model='mB'").fetchone()
            ra, rb = C.options_raw(c, oa), C.options_raw(c, ob)
            refs = {(v, k): (vid, side, how) for vid, v, k, side, how in c.execute(
                "SELECT variant_id, vintage, source_key, side_at_mint, resolution FROM reference")}
            unres = [(v, k) for v, k in c.execute("SELECT vintage, source_key FROM reference_unresolved")]
            how = Counter((v, h) for (v, _k), (_vid, _s, h) in refs.items())
            solver_105 = c.execute("SELECT seen_ck FROM response WHERE legacy_qid=105 AND model=?",
                                   (ingest.SOLVER_MODEL,)).fetchone()[0]
            math_null = c.execute("SELECT COUNT(*) FROM options_ordered WHERE is_null=1").fetchone()[0]
        finally:
            c.close()
        g.check("(1) a response's ordered options are rebuilt VERBATIM from options_ordered: mA %s / mB %s, one variant"
                % (ra, rb), ra == json.dumps(["w5", "x5", "y5"]) and rb == json.dumps(["y5", "x5", "w5"]) and ck_a == ck_b)
        un = _one(paths[1], "SELECT COUNT(*) FROM options_ordered WHERE is_null=1")
        g.check("(1) a NULL options_json (MATH) is stored as NULL, distinct from an empty string (%d NULL rows)" % un, un == 1)
        # (2) references keyed by variant, vintage, side_at_mint
        g.check("(2) v0: 29 solver_row, 10 unique_active_variant, 1 unresolved (the 2-stem qid 107); v1: 5 solver_row; got"
                " %s, unresolved %s" % (dict(sorted(how.items())), unres),
                how == Counter({("grok-reasoning-v0", "solver_row"): 29, ("grok-reasoning-v0", "unique_active_variant"): 10,
                                ("grok-reasoning-v1", "solver_row"): 5}) and unres == [("grok-reasoning-v0", "qid:107")])
        g.check("(2) the reference of qid 105 is keyed to the variant of the SOLVER's row",
                refs[("grok-reasoning-v0", "qid:105")][0] == solver_105)
        g.check("(2) side_at_mint: v0 derived from the pool file (qid 101 %s, qid 125 %s); v1 copied (%s)"
                % (refs[("grok-reasoning-v0", "qid:101")][1], refs[("grok-reasoning-v0", "qid:125")][1],
                   refs[("grok-reasoning-v1", "qid:101")][1]),
                refs[("grok-reasoning-v0", "qid:101")][1] == "EVAL" and refs[("grok-reasoning-v0", "qid:125")][1] == "NOT_LISTED"
                and refs[("grok-reasoning-v1", "qid:101")][1] == "EVAL(copied)")
        ev_side = {i: s for i, (_c, s) in side.items()}
        gref = _all(gv["path"], "SELECT item_id FROM reference")
        eref = _all(ev["path"], "SELECT item_id FROM reference")
        g.check("(2) references follow their variant's side into the views (gen %d all TRAIN/GATE, eval %d all EVAL)"
                % (len(gref), len(eref)), all(ev_side[i] != "EVAL" for (i,) in gref) and all(ev_side[i] == "EVAL" for (i,) in eref)
                and len(gref) + len(eref) == 44)
        # (3) the contract CHECK
        cpath = os.path.join(tmp, "contract_probe.db")
        cp = ro.create_new(cpath)
        cp.executescript(ingest.DDL)
        cp.execute("INSERT INTO item VALUES ('i:k','k',NULL,'corpus',1,1,0)")
        g.check("(3) variant.contract_id CHECK refuses a contract outside the closed list",
                _mutation_fails(cp, "INSERT INTO variant VALUES ('v:x','i:k','BOGUS','s','[]',NULL,0,'corpus',1,0)"))
        g.check("(3) ... and admits one on the list", not _mutation_fails(
            cp, "INSERT INTO variant VALUES ('v:y','i:k','MC_LETTER','s','[]',NULL,0,'corpus',1,0)"))
        # (5) the retired flag: not in response, not in any view, never named by split / views, refused at runtime
        for p in (paths[0], gv["path"], ev["path"]):
            cols = {r[1] for r in _all(p, "PRAGMA table_info(%s)" % ("response" if p == paths[0] else
                                                                     "response_lite" if p == gv["path"] else "response"))}
            tabs = {r[0] for r in _all(p, "SELECT name FROM sqlite_master WHERE type='table'")}
            g.check("(5) %s: no retired column in the response table, retired table present only in the corpus DB"
                    % os.path.basename(p), not (cols & set(C.RETIRED_NAMES)) and
                    (("retired_legacy_flag" in tabs) == (p == paths[0])))
        for mod in ("split.py", "views.py"):
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), mod), "r", encoding="utf-8") as f:
                src_text = f.read()
            named = [n for n in C.RETIRED_NAMES if n in src_text]
            g.check("(5) %s never names a retired column or table %s" % (mod, named), not named)
        cp.close()
        cp = ro.create_new(os.path.join(tmp, "retired_probe.db"))
        cp.execute("CREATE TABLE response (response_id TEXT, legacy_is_reserved INTEGER)")
        cp.commit()
        try:
            C.guard_retired(cp, "probe")
            refused = False
        except SystemExit:
            refused = True
        cp.close()
        g.check("(5) guard_retired REFUSES a response table that carries the retired column (split.load_corpora calls it)",
                refused)
        g.close()
        g = Gate("SELFTEST-READY-ED", say)
        # D1: the draw guard compares VALUES; both branches executed (no draw is run with the registered seed)
        reg, rseed = next(iter(split.REGISTERED_DRAWS.items()))
        dev_, lab = split.check_draw(rseed, reg)
        g.check("D1: the pinned pair (%s, %s...) is ADMITTED by check_draw (not drawn here)" % (reg, rseed[:22]),
                dev_ is False and reg in lab)
        for s_, r_, why in ((rseed + "x", reg, "a wrong seed under the pinned entry"),
                            (rseed, "ANY-STRING", "the pinned seed under another entry"),
                            ("ANY-SEED", "ANY-STRING", "an arbitrary seed and entry (probe P2)"),
                            (rseed, None, "the pinned seed without an entry"),
                            ("DEV-selftest", reg, "a DEV seed carrying a registration")):
            g.check("D1: check_draw REFUSES %s" % why, _raises(lambda: split.check_draw(s_, r_)))
        for r_, s_ in split.RETIRED_DRAWS.items():
            g.check("D1: the RETIRED draw %s (already run, never reused) is REFUSED by entry and by seed" % r_,
                    _raises(lambda: split.check_draw(s_, r_)) and _raises(lambda: split.check_draw(s_, "ARCH-V2-SPLIT-DRAW-2")))
        g.check("D1: build_split REFUSES a wrong pair before drawing",
                _raises(lambda: split.build_split(paths, build, "ANY-SEED", registration="ANY-STRING", out=quiet)))
        # D2: seed sensitivity and the golden side table
        d_a = split.compute(split.load_corpora(paths, out=quiet), "DEV-selftest")
        d_b = split.compute(split.load_corpora(paths, out=quiet), "DEV-selftest-2")
        moved = sum(1 for c_ in d_a["side_of"] if d_a["side_of"][c_] != d_b["side_of"][c_])
        i_a = independent_draw(paths, "DEV-selftest", 0.30, 0.10)
        i_b = independent_draw(paths, "DEV-selftest-2", 0.30, 0.10)
        moved_i = sum(1 for i in i_a if i_a[i] != i_b[i])
        g.check("D2: two DEV seeds move components (split.compute %d of %d components; independent_draw %d items)"
                % (moved, len(d_a["side_of"]), moved_i), moved > 0 and moved_i > 0)
        sp_c = ro.open_ro(sp["path"], require_sealed=True)
        try:
            gsha, grows = ro.table_sha(sp_c, "side")
            musr = sp_c.execute("SELECT n_components, n_eval, n_gate FROM stratum WHERE stratum_source='MUSR'").fetchone()
        finally:
            sp_c.close()
        g.check("D2: the fixture side table sha (seed DEV-selftest) equals the pinned golden %s (got %s, %d rows)"
                % (GOLDEN_FIXTURE_SIDE_SHA[:16], gsha, grows), gsha == GOLDEN_FIXTURE_SIDE_SHA)
        g.check("D2: the 5-component MUSR stratum rounds half up (EVAL 2 = floor(1.5 + 0.5), GATE 1 = floor(0.5 + 0.5);"
                " floor would give 1 / 0): got %s" % (musr,), musr == (5, 2, 1))
        # D3: the side export, verified from its text; a tampered or CRLF copy is refused
        exp = os.path.join(tmp, "side_export.tsv")
        esha, erows = split.export_side(sp["path"], exp)
        vsha, vrows = split.verify_side_export(exp, sp["path"])
        g.check("D3: the side export (%d rows) re-hashes from its TEXT to the sealed DB's table_sha" % erows,
                (esha, erows) == (vsha, vrows) == (gsha, grows))
        with open(exp, "rb") as f:
            raw = f.read()
        lines = raw.split(b"\n")
        fields = lines[2].split(b"\t")                       # the first data row; column 2 is `side`
        fields[2] = b"TRAIN" if fields[2] == b"EVAL" else b"EVAL"
        lines[2] = b"\t".join(fields)
        for name, data in (("tampered (one side flipped)", b"\n".join(lines)), ("CRLF", raw.replace(b"\n", b"\r\n"))):
            pth = os.path.join(tmp, "side_export_%s.tsv" % name[:4])
            with open(pth, "wb") as f:
                f.write(data)
            g.check("D3: verify_side_export REFUSES a %s copy" % name, _raises(lambda: split.verify_side_export(pth, sp["path"])))
        g.check("D3: export_side is write-once (an existing path is refused)",
                _raises_any(lambda: split.export_side(sp["path"], exp)))
        # D6: the solver's rendering is a MINORITY variant of qid 120; the reference follows the solver
        c = ro.open_ro(paths[0], require_sealed=True)
        try:
            solver = c.execute("SELECT seen_ck FROM response WHERE legacy_qid=120 AND model=?", (ingest.SOLVER_MODEL,)).fetchone()[0]
            modal = c.execute("SELECT seen_ck, COUNT(*) FROM response WHERE legacy_qid=120 AND model!=? AND model!="
                              "'Meta-Llama-3-70B-Instruct' GROUP BY 1 ORDER BY 2 DESC", (ingest.SOLVER_MODEL,)).fetchone()[0]
            ref = c.execute("SELECT variant_id, resolution FROM reference WHERE vintage='grok-reasoning-v0' AND"
                            " source_key='qid:120'").fetchone()
        finally:
            c.close()
        g.check("D6: qid 120's reference is keyed to the SOLVER's variant, which differs from the modal active variant"
                " (resolution %s)" % ref[1], solver != modal and ref == (solver, "solver_row"))
        # D9: the same inputs built at another absolute path give byte-identical DBs
        build2 = os.path.join(tmp, "another", "deeper", "build_path")
        os.makedirs(build2)
        p2 = [ingest.build_corpus(cv, build2, out=quiet, data_root=data_root, repo_root=os.path.join(tmp, "repo"))["path"]
              for cv in ("mmlu-pro-v2", "mc6-2026-09-11")]
        sp2 = split.build_split(p2, build2, "DEV-selftest", out=quiet)
        gv2 = views.build_view("gen", p2, sp2["path"], build2, out=quiet)
        ev2 = views.build_view("eval", p2, sp2["path"], build2, out=quiet)
        pairs = list(zip(paths + [sp["path"], gv["path"], ev["path"]], p2 + [sp2["path"], gv2["path"], ev2["path"]]))
        same = [ro.file_sha256(a) == ro.file_sha256(b) for a, b in pairs]
        g.check("D9: the five DBs built at a different absolute path are byte-identical (%d of %d)" % (sum(same), len(same)),
                all(same))
        g.close()
        g = Gate("SELFTEST-CK-CLOSE-V2", say)
        ck_close_v2_fixture_checks(g, paths, sp["path"], gv["path"], ev["path"])
        g.close()
        g = Gate("SELFTEST-R1-D7", say)
        r1_and_d7_checks(g, tmp, data_root, sp["path"])
        g.close()
        g = Gate("SELFTEST-G4", say)
        g4_loaders(gv["path"], ev["path"], g)
        r, msg = _refused(views.open_generation, "construct", paths[0])
        g.check("open_generation refuses a corpus_v2 DB (no view_kind)", r, msg[:100])
        g.close()
        g = Gate("SELFTEST-G5", say)
        g5_append_only(g, tmp)
        g.close()
        g = Gate("SELFTEST-RO", say)
        wal = os.path.join(tmp, "walled.db")
        cw = ro.create_new(wal); cw.execute("CREATE TABLE t (x)"); cw.commit(); cw.close()
        with open(wal + "-wal", "wb") as f:
            f.write(b"x" * 10)
        r, msg = _refused(ro.open_ro, wal)
        g.check("ro.open_ro refuses a DB with a non-empty -wal", r, msg[:90])
        os.remove(wal + "-wal")
        r, msg = _refused(ro.open_ro, wal, require_sealed=True)
        g.check("ro.open_ro(require_sealed) refuses an unsealed DB", r, msg[:90])
        q = ro.open_ro(wal)
        g.check("ro.open_ro sets query_only (a write through it fails)", _mutation_fails(q, "INSERT INTO t VALUES (1)"))
        q.close()
        g.check("split refuses a non-DEV seed without a registration",
                _raises(lambda: split.build_split(paths, build, "42", out=quiet)))
        forced = Gate("FORCED", quiet)
        forced.check("a deliberately failing check", False)
        g.check("a gate with a failing check REFUSES on close (raise SystemExit, the -O-proof branch)", _raises(forced.close))
        g.close()
    finally:
        _rmtree(tmp)
    out("[SELFTEST] data_v2: ALL PASS (%d checks; synthetic fixture; no DB of record opened)" % total["checks"])
    return 0


def _iid(text):
    return "i:" + C.split_side.stem_key(text)


def ast_witness(path, forbid_calls=(), forbid_name_parts=(), forbid_imports=(), forbid_attrs=()):
    """Static witness over a module's AST (docstrings and comments are not code): the forbidden calls, identifiers,
    imported modules and attribute uses found. Returns a sorted list of findings ([] = clean)."""
    import ast
    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    hits = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbid_calls:
            hits.add("call %s()" % node.func.id)
        # any REFERENCE to a forbidden builtin counts, not only a call: sorted(..., key=hash) uses hash() too
        if isinstance(node, ast.Name) and node.id in forbid_calls:
            hits.add("reference to %s" % node.id)
        names = []
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.arg):
            names.append(node.arg)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
            if isinstance(node.value, ast.Name) and (node.value.id, node.attr) in forbid_attrs:
                hits.add("attribute %s.%s" % (node.value.id, node.attr))
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names.append(node.name)
        for n in names:
            for part in forbid_name_parts:
                if part in n.lower():
                    hits.add("identifier %s" % n)
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in forbid_imports:
                    hits.add("import %s" % a.name)
        if isinstance(node, ast.ImportFrom):
            mods = [node.module or ""] + [a.name for a in node.names]
            for m_ in mods:
                if m_ and m_.split(".")[-1] in forbid_imports:
                    hits.add("from-import %s" % m_)
    return sorted(hits)


PASSAGE_AST = {"forbid_calls": ("hash", "id"), "forbid_name_parts": ("seed", "random", "time"),
               "forbid_imports": ("random", "time", "os", "secrets", "datetime")}
INDEPENDENT_AST = {"forbid_imports": ("split", "passage_closure", "ingest", "views", "gates", "content_closure"),
                   "forbid_attrs": (("_common", "pc"), ("_common", "cc"), ("C", "pc"), ("C", "cc")),
                   "forbid_calls": ("hash",)}


def ck_close_v2_fixture_checks(g, paths, split_path, gen_path, eval_path):
    """K1-K5 executed on the synthetic fixture (the registration's criteria; ARCH-V2-CK-CLOSE-V2)."""
    sp = ro.open_ro(split_path, require_sealed=True)
    try:
        meta = dict(sp.execute("SELECT key, value FROM meta"))
        excl = [i for (i,) in sp.execute("SELECT item_id FROM excluded_u")]
        edges = {k: set() for k in "POD"}
        for k, a, b in sp.execute("SELECT kind, item_a, item_b FROM closure_edge"):
            edges[k].add((a, b))
        comp = dict(sp.execute("SELECT item_id, component_id FROM side"))
    finally:
        sp.close()

    def joined(kind, x, y):
        a, b = sorted((_iid(K3[x]) if x in K3 else x, _iid(K3[y]) if y in K3 else y))
        return (a, b) in edges[kind]
    # K1
    q_only = _iid(K3_QUARANTINED_ONLY)
    in_views = sum(_one(p, "SELECT COUNT(*) FROM item WHERE item_id='%s'" % q_only) for p in (gen_path, eval_path))
    g.check("K1: U excludes exactly the quarantined-only item (%d excluded; digest %s...), which is in no side and no view"
            % (len(excl), meta.get("u_digest", "")[:16]), excl == [q_only] and q_only not in comp and in_views == 0)
    # K3 P
    g.check("K3 P: a 20-token unmasked run JOINS", joined("P", "P20a", "P20b"))
    g.check("K3 P: a 19-token run is REFUSED", not joined("P", "P19a", "P19b"))
    g.check("K3 P: a 24-token run containing ONE masked shingle (df 7 > R 6) is REFUSED", not joined("P", "PMa", "PMb"))
    # K3 O
    oe = [_iid(t) for t, _o in K3_MMLU_ROWS if t.startswith("Options case ")]
    ie, if_, ig, ih, ii, ij = oe
    g.check("K3 O: 20 shared option tokens JOIN (and no P edge between those stems)",
            (min(ie, if_), max(ie, if_)) in edges["O"] and (min(ie, if_), max(ie, if_)) not in edges["P"])
    g.check("K3 O: 19 shared option tokens are REFUSED", (min(ig, ih), max(ig, ih)) not in edges["O"])
    g.check("K3 O: 24 shared option tokens with one masked shingle (df 7) are REFUSED", (min(ii, ij), max(ii, ij)) not in edges["O"])
    # K3 BBH: 40 items in the task, 5% = 2 items
    bj = sorted(_iid(K3_BBH_STEMS[k]) for k in (30, 31))
    bt = sorted(_iid(K3_BBH_STEMS[k]) for k in (32, 33, 34))
    g.check("K3 BBH: a run held by 2 of the task's 40 items (not more than 5%) JOINS", tuple(bj) in edges["P"])
    g.check("K3 BBH: a run held by 3 of 40 (more than 5%) is MASKED although df 3 <= R 6 (the task's 5%, not R) and"
            " although 3 <= 5% of all 70 BBH items (the TASK's 5%, not the source's)",
            not any((a, b) in edges["P"] for a in bt for b in bt if a < b))
    # READY_ck_close_v2 D2: the BBH mask is PER TASK (stratum), not source-wide
    bw = sorted(_iid(K3_BBH2_STEMS[k]) for k in (10, 11))
    g.check("D2/M3: in a SECOND BBH task (30 items), a run held by 2 of 30 (more than 5% of the task) is MASKED, although"
            " a source-wide mask (70 BBH items, 5% = 3.5) would unmask it", tuple(bw) not in edges["P"])
    # df exactly R = 6 is unmasked; the two-variant item counts ONCE in df
    v6 = _iid(K3["V6a"])
    six = [v6] + [_iid(t) for t in K3_DF6_OTHERS]
    n_var = _one(paths[0], "SELECT COUNT(*) FROM variant WHERE item_id='%s'" % v6)
    n_stem = len({t for (t,) in _all(paths[0], "SELECT stem FROM variant WHERE item_id='%s'" % v6)})
    g.check("D2/M2: the item %s has TWO variants with two raw stems (%d variants, %d stems) and ONE item id"
            % (v6[:14], n_var, n_stem), n_var == 2 and n_stem == 2 and _iid(K3["V6b"]) == v6)
    g.check("D2/M3c+M2: a run held by EXACTLY 6 items (df 6, not > R 6; the two-variant item counted once) JOINS all six"
            " into one component", len({comp[i] for i in six}) == 1 and tuple(sorted((v6, six[1]))) in edges["P"])
    g.check("D2/M11: an UPPER-CASE rendering joins its lower-case twin through casefold (two distinct items)",
            _iid(K3["UPa"]) != _iid(K3["UPb"]) and joined("P", "UPa", "UPb"))
    # K3 D
    d1, d2, d3 = _iid(K3["D1"]), _iid(K3["D2"]), _iid(K3["D3"])
    g.check("K3 D: D joins the \\textdegree and the ° renderings (and P does not: runs of 13 tokens either side)",
            joined("D", "D1", "D2") and not joined("P", "D1", "D2"))
    g.check("K3 D: the U+FFFD rendering tokenises like ° and is joined by P (26 tokens), not by D (d() does not touch"
            " U+FFFD); the triple ends in ONE component", joined("P", "D2", "D3") and not joined("D", "D2", "D3")
            and comp[d1] == comp[d2] == comp[d3])
    stems = dict(_all(paths[0], "SELECT item_id, stem_key FROM item"))
    g.check("K3 D: no key change: the three items keep three distinct ids, each id = 'i:' + its own norm-v1 stem_key,"
            " NORMALISER_VERSION %s" % meta.get("normaliser"),
            len({d1, d2, d3}) == 3 and all(stems[i] == i[2:] for i in (d1, d2, d3))
            and all(i == "i:" + stems[i] for i in comp if i in stems) and meta.get("normaliser") == "norm-v1")
    # K2 static witnesses (the fresh-process PYTHONHASHSEED check runs in g2_split)
    pc_hits = ast_witness(os.path.join(C.ANALYSIS, "passage_closure.py"), **PASSAGE_AST)
    g.check("K2: passage_closure.py calls no hash() / id(), reads no seed, random or clock (AST witness) %s" % pc_hits, not pc_hits)
    ind_hits = ast_witness(os.path.join(os.path.dirname(os.path.abspath(__file__)), "independent.py"), **INDEPENDENT_AST)
    g.check("the second implementation (data_v2/independent.py) shares no code with split / passage_closure (AST) %s"
            % ind_hits, not ind_hits)
    # pool rows: every scope named exactly once; the merge of two scopes sharing one id, executed directly
    scopes = [s for (sc,) in _all(split_path, "SELECT scope FROM pool") for s in sc.split(" + ")]
    g.check("pool table: the scopes %s are each recorded exactly once" % sorted(scopes),
            sorted(scopes) == sorted(["all corpora", "mc6-2026-09-11", "mmlu-pro-v2"]))
    pl = split.merge_pool({}, "pv2dev_x", "all corpora", 3, 5)
    split.merge_pool(pl, "pv2dev_x", "mc6-2026-09-11", 3, 4)
    g.check("merge_pool: two scopes with one component list share ONE row, both kept %s" % (pl["pv2dev_x"],),
            pl == {"pv2dev_x": (["all corpora", "mc6-2026-09-11"], 3, {"all corpora": 5, "mc6-2026-09-11": 4})})
    g.check("merge_pool REFUSES one id naming two component counts",
            _raises(lambda: split.merge_pool(dict(pl), "pv2dev_x", "mmlu-pro-v2", 2, 2)))
    # K4 + K5 recorded in the meta
    v2 = json.loads(meta["checks"])["v2"]
    g.check("K4: 0 closure edges cross the sides (%s); K5 figures recorded (components %d, edges %s, band %s)"
            % (v2["crossing"], v2["after_u"]["components"], v2["edges"], v2["band_15_19"]),
            not any(v2["crossing"].values()) and v2["band_15_19"]["P"] >= 2 and v2["band_15_19"]["O"] >= 1)


def r1_and_d7_checks(g, tmp, data_root, split_path):
    """READY_ck_close_v2 D3 (R1 fails closed) and D7 (K1 against a superseded split), both branches executed."""
    import subprocess
    from . import build
    quiet = lambda s: None
    # D7: a synthetic "superseded draw" in a scratch root: the fixture split's side table exported under the draw's name
    root = os.path.join(tmp, "d7root")
    mdir = os.path.join(root, "data_v2", "manifests")
    os.makedirs(mdir)
    tsv = os.path.join(mdir, SUPERSEDED_DRAW + "_side.tsv")
    tsha, _n = split.export_side(split_path, tsv)
    with open(os.path.join(mdir, SUPERSEDED_DRAW + ".json"), "w", encoding="utf-8") as f:
        json.dump({"side_export": {"table_sha": tsha}}, f)
    side_of = dict(_all(split_path, "SELECT item_id, side FROM side"))
    pick = sorted(side_of)[:7]
    want, absent = u_side_counts(pick, side_of)
    ok_gate = Gate("D7+", quiet)
    superseded_u_check(ok_gate, pick, root=root, expected=want)
    g.check("D7: the superseded-split check PASSES when the excluded items sit exactly as expected (%s)" % want,
            not ok_gate.fails and absent == 0)
    bad_gate = Gate("D7-", quiet)
    superseded_u_check(bad_gate, pick + ["i:not-in-the-old-split"], root=root, expected=want)
    g.check("D7: ... and FAILS on an excluded item absent from the old split, or on other counts (%d failing check)"
            % len(bad_gate.fails), len(bad_gate.fails) == 1)
    bad2 = Gate("D7x", quiet)
    superseded_u_check(bad2, pick, root=root, expected=dict(SUPERSEDED_U_SIDES))
    g.check("D7: ... and FAILS against the registration's 523 / 228 / 89 on the fixture", len(bad2.fails) == 1)
    with open(tsv, "rb") as f:
        raw = f.read()
    with open(tsv, "wb") as f:
        f.write(raw.replace(b"\n", b"\r\n"))                     # what a core.autocrlf checkout of the LF blob gives
    crlf_gate = Gate("D7crlf", quiet)
    superseded_u_check(crlf_gate, pick, root=root, expected=want)
    g.check("D7: a CRLF working-tree copy of the committed LF export PASSES (verified on its LF rendering)",
            not crlf_gate.fails)
    with open(tsv, "wb") as f:
        f.write(raw.replace(b"\tEVAL\t", b"\tTRAIN\t", 1))
    t_gate = Gate("D7t", quiet)
    superseded_u_check(t_gate, pick, root=root, expected=want)
    g.check("D7: a tampered superseded export FAILS (its text sha differs from its header; %d failing check)"
            % len(t_gate.fails), len(t_gate.fails) == 1 and "verifies from its LF text" in t_gate.fails[0])
    # D3: the R1 verdict, pure branches
    clean = build.r1_verdict({"a.db": "1"}, {"a.db": "1"}, [{"stage": "launch", "foreign": []}])
    changed = build.r1_verdict({"a.db": "1"}, {"a.db": "2"}, [{"stage": "launch", "foreign": []}])
    foreign = build.r1_verdict({"a.db": "1"}, {"a.db": "1"}, [{"stage": "during", "foreign": [[4242, "python.exe", "x"]]}])
    g.check("D3: r1_verdict is CLEAN with unchanged inputs and no foreign process", clean == (False, []))
    g.check("D3: r1_verdict is VOID on a CHANGED input (%s)" % changed[1], changed[0] and "CHANGED" in changed[1][0])
    g.check("D3: r1_verdict is VOID on a FOREIGN process (%s)" % foreign[1], foreign[0] and "4242" in foreign[1][0])
    # D3 end to end: the real build.main on the fixture, with a foreign python process alive during the whole run
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
    try:
        man = os.path.join(tmp, "r1man")
        env = dict(os.environ, TAXOARENA_DATA_ROOT=data_root)
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.py"),
                            "--seed", "DEV-r1-selftest", "--out-dir", os.path.join(tmp, "r1build"), "--manifest-dir", man,
                            "--repo-root", os.path.join(tmp, "repo")], capture_output=True, text=True, env=env)
    finally:
        sleeper.kill()
        sleeper.wait()
    mp = os.path.join(man, "DEV_DEV-r1-selftest.json")
    m = json.load(open(mp, encoding="utf-8")) if os.path.isfile(mp) else {}
    named = any(str(sleeper.pid) in x for x in m.get("r1_void_reasons", []))
    g.check("D3: the build run with a FOREIGN python process alive EXITS 3 and writes a manifest marked VOID naming the"
            " process (rc %d, r1_void %s, of_record %r, pid %d named %s)" % (r.returncode, m.get("r1_void"),
                                                                           (m.get("of_record") or "")[:30], sleeper.pid, named),
            r.returncode == 3 and m.get("r1_void") is True and (m.get("of_record") or "").startswith("VOID (R1)") and named)


def _straddle(data, res):
    """A tampered copy of res in which the union's copy of mmlu_pro row 1 (the cross-corpus twin) is given its own
    component on the other side: the same stem_key then sits on both sides, which content_closure must refuse."""
    t = {"comp_of": dict(res["comp_of"]), "side_of": dict(res["side_of"])}
    k1 ="i:" + C.split_side.stem_key("Question number 1 about math?")
    # items are global, so a straddle is simulated at the UNIT level: rewrite one union unit's item to a fresh item
    fresh = "i:tampered"
    for uid, u in data["units"].items():
        if u["corpus"] == "mc6-2026-09-11" and u["item"] == k1:
            u["item"] = fresh
            break
    t["comp_of"][fresh] = "c:tampered"
    t["side_of"]["c:tampered"] = "TRAIN" if res["side_of"][res["comp_of"][k1]] == "EVAL" else "EVAL"
    data["items"][fresh] = "tampered"
    return t


def _raises(fn):
    try:
        fn()
        return False
    except SystemExit:
        return True


def _raises_any(fn):
    try:
        fn()
        return False
    except (SystemExit, OSError):
        return True


def _one(path, sql):
    c = ro.open_ro(path)
    try:
        return c.execute(sql).fetchone()[0]
    finally:
        c.close()


def _all(path, sql):
    c = ro.open_ro(path)
    try:
        return c.execute(sql).fetchall()
    finally:
        c.close()


def main(argv):
    """--transcript PATH writes every printed line to PATH, opened with mode "x" (written once), even on a failure."""
    lines = []

    def out(s):
        print(s, flush=True)
        lines.append(s)
    if argv and argv[0] == "--edge-sha":
        # K2 witness: the edge-set sha16 of the given sealed corpora, computed in THIS process (the caller sets
        # PYTHONHASHSEED); nothing else is printed on the EDGE_SHA16 line
        data = split.load_corpora(argv[1:], out=lambda s: None)
        print("EDGE_SHA16 %s" % data["closure_v2"]["edge_set_sha16"])
        return 0
    tr = argv[argv.index("--transcript") + 1] if "--transcript" in argv else None
    if tr is not None and os.path.exists(tr):
        C._refuse("%s exists: a transcript is written once" % tr)
    try:
        if "--selftest" in argv:
            return selftest(out)
        if "--build-dir" in argv:
            return run_build_dir(argv[argv.index("--build-dir") + 1], out)
        print(__doc__)
        return 2
    finally:
        if tr is not None:
            with open(tr, "x", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
