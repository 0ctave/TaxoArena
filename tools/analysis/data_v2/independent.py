"""data_v2.independent: the SECOND implementation of the v2 draw (CK-CLOSE-v2), for gate G2 (READY_archv2_ED D2; the
ARCH-V2-CK-CLOSE-V2 brief: "gates.independent_draw must implement U and P / O / D INDEPENDENTLY").

It shares NO code with data_v2.split or passage_closure (gates.py --selftest parses this file's AST and refuses an import of
split / passage_closure / ingest / views / gates or any use of common.pc / common.cc). It reads the sealed corpus DBs with
its own SQL (through data_v2.ro) and uses only split_side.stem_key (the key function of record, via data_v2.common) for D.

The rule, restated from the registration (docs/judge_v2_program.md L16101-L16130) and written apart:
  U   keep an item iff it has a corpus source_row or a response by an ACTIVE model
  P/O a shingle = 8 consecutive tokens of re.findall(r"\\w+", text.casefold()); its identity here is sha256 over the tokens
      joined by U+001F (the registration's allowed alternative to exact tuples); df = distinct universe items holding it
      (per channel: stems for P, option strings for O = options_sorted_json joined by single spaces). Masked for an item:
      BBH item (own stratum source BBH) iff held by MORE THAN 5% of the universe items of its own stratum; any other item
      iff df > 6. A pair counts a shingle only when it is unmasked for BOTH items. Two items are joined when two of their
      texts share, ON ONE DIAGONAL, at least 20 consecutive equal tokens whose every shingle is unmasked. METHOD (different
      from passage_closure's diagonal counting): candidate pairs come from shared unmasked shingles; for each candidate
      pair of texts and each offset seen, the two token lists are compared directly, token by token, along that diagonal.
  D   d(s): "\\s*\\textdegree({})?\\s*" -> "°", then "\\s*°\\s*" -> "°"; items whose stems share split_side.stem_key(d(s))
      are joined (reported as GROUPS, not as chains)
  then: components over items joined by the stem, declared families, the legacy question-id families of ACTIVE models (and
  the union qid's own row), and P / O / D; component id "c:" + smallest stem_key; stratum = modal (source, domain) of
  the corpus rows, else active responses, else quarantined ones, ties to the smallest; rank = sha256("taxoarena-split-v2"
  U+001F seed U+001F component id); per stratum EVAL = floor(r n + 0.5), GATE = min(floor(g n + 0.5), n - EVAL).
"""
import hashlib
import json
import re
from collections import Counter, defaultdict

from . import common as _common
from . import ro

_WORD = re.compile(r"\w+")
_TEXTDEG = re.compile(r"\s*\\textdegree(\{\})?\s*")
_DEGSP = re.compile(r"\s*°\s*")
MIN_RUN, SH, CAP, BBH_PCT = 20, 8, 6, 0.05


def _toks(s):
    return _WORD.findall(s.casefold())


def _dnorm(s):
    return _DEGSP.sub("°", _TEXTDEG.sub("°", s))


def _digests(toks):
    return [hashlib.sha256("\u001f".join(toks[p:p + SH]).encode("utf-8")).digest() for p in range(len(toks) - SH + 1)]


def read_corpora(corpus_paths):
    stem, fam, stems, opts = {}, [], defaultdict(set), defaultdict(set)
    v_rows, v_act, v_quar = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    for path in corpus_paths:
        c = ro.open_ro(path, require_sealed=True)
        try:
            cv = c.execute("SELECT value FROM meta WHERE key='corpus_version'").fetchone()[0]
            status = dict(c.execute("SELECT model, status FROM model_registry"))
            for iid, sk, f in c.execute("SELECT item_id, stem_key, family_id FROM item"):
                stem[iid] = sk
                if f:
                    fam.append(("F" + f, iid))
            for iid, src, dom in c.execute("SELECT item_id, source, domain FROM source_row"):
                v_rows[iid][(src, dom if dom is not None else "")] += 1
            for iid, st, oj in c.execute("SELECT item_id, stem, options_sorted_json FROM variant"):
                stems[iid].add(st)
                lst = json.loads(oj)
                if lst:
                    opts[iid].add(" ".join(lst))
            own_row = {}
            if cv == "mc6-2026-09-11":
                own_row = dict(c.execute("SELECT upstream_pk, item_id FROM source_row WHERE corpus_table='corpus_questions'"))
            qitems = defaultdict(set)
            for q, model, iid, src, cat in c.execute("SELECT legacy_qid, model, item_id, source, category FROM response"):
                if status[model] == "ACTIVE":
                    v_act[iid][(src, cat)] += 1
                    qitems[q].add(iid)
                else:
                    v_quar[iid][(src, cat)] += 1
            for q, its in qitems.items():
                if q in own_row:
                    its = its | {own_row[q]}
                for iid in its:
                    fam.append(("Q%s|%s" % (cv, q), iid))
        finally:
            c.close()
    return {"stem": stem, "fam": fam, "stems": stems, "opts": opts, "v_rows": v_rows, "v_act": v_act, "v_quar": v_quar}


def _vote(counters, items):
    for src in counters:
        tally = Counter()
        for i in items:
            tally.update(src.get(i, {}))
        if tally:
            best = max(tally.values())
            return min(k for k, v in tally.items() if v == best), len(tally)
    return None, 0


def _channel_edges(universe, texts, own_stratum):
    """Edges and 15-19 band pairs for one channel, by candidate pairs + a direct walk along each diagonal."""
    toks = {i: [t for t in (_toks(x) for x in sorted(texts[i])) if len(t) >= SH] for i in universe}
    digs = {i: [_digests(t) for t in toks[i]] for i in universe}
    df = Counter()
    for i in universe:
        df.update({d for ds in digs[i] for d in ds})
    size = Counter(own_stratum[i] for i in universe)
    sdf = defaultdict(Counter)
    for i in universe:
        if own_stratum[i][0] == "BBH":
            sdf[own_stratum[i]].update({d for ds in digs[i] for d in ds})

    def unmasked(i, d):
        st = own_stratum[i]
        if st[0] == "BBH":
            return not (sdf[st][d] > BBH_PCT * size[st])
        return not (df[d] > CAP)
    holders = defaultdict(set)
    for i in sorted(universe):
        for ds in digs[i]:
            for d in ds:
                if df[d] > 1 and unmasked(i, d):
                    holders[d].add(i)
    cands = set()
    for d, hs in holders.items():
        if len(hs) > 1:
            hs = sorted(hs)
            for x in range(len(hs)):
                for y in range(x + 1, len(hs)):
                    cands.add((hs[x], hs[y]))
    edges, band = set(), set()
    for a, b in sorted(cands):
        best = 0
        for ta, da in zip(toks[a], digs[a]):
            ua = [unmasked(a, d) and unmasked(b, d) for d in da]
            for tb, db in zip(toks[b], digs[b]):
                where = defaultdict(list)
                for j, d in enumerate(db):
                    where[d].append(j)
                offsets = sorted({i - j for i, d in enumerate(da) for j in where.get(d, ())})
                for off in offsets:
                    # walk the diagonal token by token: i in ta, i - off in tb
                    i0 = max(0, off)
                    i1 = min(len(ta), len(tb) + off)
                    i = i0
                    while i < i1:
                        if ta[i] != tb[i - off]:
                            i += 1
                            continue
                        s = i
                        while i < i1 and ta[i] == tb[i - off]:
                            i += 1
                        # equal-token segment [s, i); valid runs = maximal stretches of shingle starts unmasked for both
                        run = 0
                        for p in range(s, i - SH + 1):
                            ok = ua[p] and (p - off) < len(db) and unmasked(b, db[p - off])
                            run = run + 1 if ok else 0
                            if run:
                                best = max(best, run + SH - 1)
        if best >= MIN_RUN:
            edges.add((a, b))
        elif best >= 15:
            band.add((a, b))
    return edges, band


def closure(data):
    """U, the per-item strata, and the P / O / D closure, computed here. Returns a dict."""
    universe = {i for i in data["stem"] if data["v_rows"].get(i) or data["v_act"].get(i)}
    excluded = sorted(set(data["stem"]) - universe)
    own = {}
    for i in universe:
        own[i] = _vote((data["v_rows"], data["v_act"], data["v_quar"]), [i])[0]
    p, pband = _channel_edges(universe, data["stems"], own)
    o, oband = _channel_edges(universe, data["opts"], own)
    groups = defaultdict(set)
    for i in universe:
        for s in data["stems"][i]:
            groups[_common.split_side.stem_key(_dnorm(s))].add(i)
    dgroups = sorted(tuple(sorted(g)) for g in groups.values() if len(g) > 1)
    return {"universe": universe, "excluded": excluded, "P": sorted(p), "O": sorted(o), "D_groups": dgroups,
            "band": {"P": len(pband), "O": len(oband)}}


def draw(corpus_paths, seed, eval_ratio, gate_ratio, data=None, cl=None):
    """{item_id: (component_id, side)} over the universe, plus the closure; everything computed in this module."""
    data = data or read_corpora(corpus_paths)
    cl = cl or closure(data)
    uni = cl["universe"]
    parent = {}

    def root(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], parent[x])
            x = parent[x]
        return x

    def join(a, b):
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    stem = data["stem"]
    for f, iid in data["fam"]:
        if iid in uni:
            join("f:" + f, "i:" + stem[iid])
    for a, b in cl["P"] + cl["O"]:
        join("i:" + stem[a], "i:" + stem[b])
    for g in cl["D_groups"]:
        for x in g[1:]:
            join("i:" + stem[g[0]], "i:" + stem[x])
    comps = defaultdict(list)
    for iid in uni:
        comps[root("i:" + stem[iid])].append(iid)
    comp_of, strat = {}, {}
    for its in comps.values():
        cid = "c:" + min(stem[i] for i in its)
        strat[cid] = _vote((data["v_rows"], data["v_act"], data["v_quar"]), its)[0]
        for i in its:
            comp_of[i] = cid
    by = defaultdict(list)
    for cid, st in strat.items():
        by[st].append(cid)
    side = {}
    for st, cids in by.items():
        cids.sort(key=lambda x: hashlib.sha256(("taxoarena-split-v2\u001f%s\u001f%s" % (seed, x)).encode("utf-8")).hexdigest())
        n = len(cids)
        ne = int(eval_ratio * n + 0.5)
        ng = min(int(gate_ratio * n + 0.5), n - ne)
        for k, cid in enumerate(cids):
            side[cid] = "EVAL" if k < ne else ("GATE" if k < ne + ng else "TRAIN")
    return {i: (comp_of[i], side[comp_of[i]]) for i in uni}, cl
