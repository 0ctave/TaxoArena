"""Read-only loaders and the two edge builders.

PATHS resolve under TAXOARENA_DATA_ROOT when set (a worktree carries no DB), else under the repo root. Every DB goes
through ro.open_ro (pool_guard's -wal / -journal refusal, then mode=ro&immutable=1). snapshots_frozen.db and the 20NG DB
are refused by name.

stack_judge is NEVER imported (its open_cache() is the read-write open of STACK-JUDGE-RO-CACHE): import_sb() installs a
stub in sys.modules["stack_judge"] BEFORE systematic_budget is imported (the CERT-UNDER-FILTER pattern, ruling R3). The
stub admits only what systematic_budget.build() does to it (set PROMPT / ALL_X12; call open_cache()), and its
open_cache() returns ro.open_ro(<the cache the caller authorised>) - nothing else.

THE TWO BUILDERS
  edges_exact  the v1 configuration: a line-for-line re-statement of systematic_budget.build()'s per-anchor loop (B =
               300, random.Random(42), the same draw order, judge_free_tests.board_from -> rejudge_grok.mm_fit, the
               200-row floor), fed by the read-only loader instead of build()'s own opens. Its fidelity is not assumed:
               the replay's identity leg runs the RECORDED build() (under ro shims) and requires the two edge tables to
               be BYTE-IDENTICAL, and build()'s LF source must hash to BUILD_SRC_SHA16 (the pin ruled for
               CERT-UNDER-FILTER, R4) or the identity leg refuses.
  edges_fast   the simulator's builder: numpy question-bootstrap boards (bt.mm_fit_batch), a named numpy stream per
               anchor, the same edge fields; optional per-order and length-adjusted boards on the SAME question draws,
               and a match-level bootstrap for DEFF.
"""
import ast
import hashlib
import os
import random
import sys
import types
from collections import Counter, defaultdict

import numpy as np

from . import bt, ro

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))           # tools/analysis
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
X12DIR = os.path.join("experiment_results", "x12_crossdomain")
PATHS = dict(
    eval="mmlu_pro_dataset_cache_v2.db",
    multicorpus="multicorpus_cache_v1.db",
    snapshots="snapshots.db",
    grok=os.path.join(X12DIR, "grok_calib.db"),
    x12=os.path.join(X12DIR, "stack_v2_promptv2_x12all.db"),
    x20=os.path.join(X12DIR, "stack_v2_promptv2_x20.db"),
    kotlin=os.path.join("experiment_results", "judge_wiring", "board", "kotlin_c0d3f708cbc3930e.db"),
    promoted=os.path.join("experiment_results", "promoted"),
)
TREE = "bareq512_s42"
QUARANTINED = "Meta-Llama-3-70B-Instruct"        # CONTEXT.md section 4 rule 6
BUILD_SRC_SHA16 = "128baa007a44a219"             # systematic_budget.build LF source (CERT-UNDER-FILTER ruling R4)
WITNESS = defaultdict(int)                       # execution witness of the NEW code paths
MUTANT = None                                    # SELFTEST-ONLY switch (None in every real run): bbh_not_missing


def path(key, root=None):
    return os.path.join(root or DATA_ROOT, PATHS[key])


# ------------------------------------------------------------------------------------ systematic_budget import
class StubRefusal(RuntimeError):
    pass


class _StackJudgeStub(types.ModuleType):
    _admitted = ("PROMPT", "ALL_X12", "open_cache", "AUTHORISED", "OPENS")

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        raise StubRefusal("stack_judge.%s refused: this process never imports stack_judge" % name)

    def __setattr__(self, name, value):
        if name.startswith("__") or name in self._admitted:
            return types.ModuleType.__setattr__(self, name, value)
        raise StubRefusal("stack_judge.%s = ... refused" % name)


def _stub_open_cache():
    stub = sys.modules["stack_judge"]
    if not stub.AUTHORISED:
        raise StubRefusal("stack_judge.open_cache() refused: no cache authorised")
    stub.OPENS += 1
    return ro.open_ro(stub.AUTHORISED)


def import_sb():
    existing = sys.modules.get("stack_judge")
    if existing is not None and not isinstance(existing, _StackJudgeStub):
        raise SystemExit("[ARCHV2] the real stack_judge module is loaded in this process; refused (it opens its cache"
                         " read-write)")
    if existing is None:
        stub = _StackJudgeStub("stack_judge")
        stub.AUTHORISED = None
        stub.OPENS = 0
        stub.open_cache = _stub_open_cache
        sys.modules["stack_judge"] = stub
    import systematic_budget as sb                  # noqa: E402  (after the stub, by design)
    if not isinstance(sys.modules["stack_judge"], _StackJudgeStub):
        raise SystemExit("[ARCHV2] stack_judge stub displaced")
    return sb


def authorise_cache(p):
    sys.modules["stack_judge"].AUTHORISED = p


def func_source(pyfile, name):
    txt = open(pyfile, encoding="utf-8").read().replace("\r\n", "\n")
    for node in ast.parse(txt).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(txt, node)
    raise SystemExit("[PIN] %s has no top-level function %s" % (pyfile, name))


def build_pin(sb):
    got = hashlib.sha256(func_source(os.path.abspath(sb.__file__), "build").encode("utf-8")).hexdigest()[:16]
    return got, got == BUILD_SRC_SHA16


def file_identity(p):
    raw = open(p, "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(),
                sha256_lf16=hashlib.sha256(lf).hexdigest()[:16],
                worktree="LF" if raw == lf else "CRLF sha256-crlf16:%s" % hashlib.sha256(raw).hexdigest()[:16])


# -------------------------------------------------------------------------------------------------- the key
def table_columns(con, table):
    return [r[1] for r in con.execute("PRAGMA table_info(%s)" % table)]


class KeyTable:
    """The key and the extracted answers of one corpus DB, read ONCE: dict views (exactly as systematic_budget.build
    reads them: K = int(is_correct or 0), P = (pred or '').strip().upper()[:1], last row wins) and array views."""

    def __init__(self, db, models=None, with_len=True, stratum="category", missing_sources=()):
        con = ro.open_ro(db)
        cols = table_columns(con, "eval_results")
        sel = "question_id, model_name, pred, is_correct" + (", LENGTH(model_output)" if with_len and "model_output" in cols else ", NULL")
        sel += ", category" if "category" in cols else ", NULL"
        self.K = defaultdict(dict); self.P = defaultdict(dict); self.L = defaultdict(dict)
        cats = defaultdict(Counter)
        seen_models = set()
        for q, m, pr, c, ln, cat in con.execute("SELECT %s FROM eval_results" % sel):
            seen_models.add(m)
            if cat is not None:
                cats[q][cat.strip().lower()] += 1
            if models is not None and m not in models:
                continue
            self.K[q][m] = int(c or 0)
            self.P[q][m] = (pr or "").strip().upper()[:1]
            if ln is not None:
                self.L[q][m] = int(ln)
        # eval_results.category is NOT one value per question id (key_subanchor_scale.py: 6,624 ids carry more than
        # one): the anchor is the MODAL normalised (strip, lower) value over ALL models' rows, ties broken
        # lexicographically; the count of ids with more than one normalised value is kept as a data check.
        self.cat = {q: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0] for q, c in cats.items()}
        self.cat_conflicts = sum(1 for c in cats.values() if len(c) > 1)
        self.strata = dict(self.cat)
        if stratum == "source_domain" and "corpus_questions" in [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")]:
            self.strata = {q: "%s/%s" % (s, d) for q, s, d in con.execute("SELECT question_id, source, domain FROM corpus_questions")}
        con.close()
        # ruling 2 (83f431b): every BBH and MuSR extracted answer is MISSING (BBH's pred is a raw argument dump; MuSR's
        # contradicts is_correct in 19.7% of rows); convention A keeps such a match, and with equal keys it is NONDEC
        self.missing_sources = tuple(s.upper() for s in (missing_sources or ()))
        self.n_missing = 0
        if self.missing_sources:
            miss = self.missing_sources if MUTANT != "bbh_not_missing" else ()
            for q, s in self.strata.items():
                if s.split("/")[0].upper() in miss and q in self.P:
                    for m in self.P[q]:
                        self.P[q][m] = ""
                        self.n_missing += 1
        self.all_models = sorted(seen_models)
        self.models = sorted(models) if models is not None else self.all_models
        self.db = db

    def arrays(self, models, qids):
        mi = {m: k for k, m in enumerate(models)}
        Q = len(qids)
        K = -np.ones((Q, len(models)), dtype=np.int8)
        P = np.zeros((Q, len(models)), dtype="<U1")
        L = np.full((Q, len(models)), np.nan)
        for r, q in enumerate(qids):
            for m, v in self.K.get(q, {}).items():
                if m in mi:
                    K[r, mi[m]] = v
            for m, v in self.P.get(q, {}).items():
                if m in mi:
                    P[r, mi[m]] = v
            for m, v in self.L.get(q, {}).items():
                if m in mi:
                    L[r, mi[m]] = v
        return K, P, L


# ------------------------------------------------------------------------------------------- verdicts, routing
def load_verdicts(db):
    """Rows in the cache's own order: (model_a, model_b, qid, winner, invalid, vote1, vote2_raw)."""
    con = ro.open_ro(db)
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")]
    if "verdicts" not in tables:
        con.close()
        raise SystemExit("[ARCHV2] %s has no 'verdicts' table (tables: %s)" % (db, ", ".join(tables)))
    cols = table_columns(con, "verdicts")
    v1 = "vote1" if "vote1" in cols else "NULL"
    v2 = "vote2_raw" if "vote2_raw" in cols else "NULL"
    rows = list(con.execute("SELECT model_a, model_b, qid, winner, invalid, %s, %s FROM verdicts" % (v1, v2)))
    con.close()
    return rows, ("vote1" in cols and "vote2_raw" in cols)


def load_routing(tree=TREE, root=None):
    """(route q -> leaf, anchor_of leaf -> anchor label): rubric_512's CSV reader and anchor_fn (pure), the graph read
    through open_ro(snapshots.db) (the same SELECT as rubric_512.load_graph)."""
    import json
    import rubric_512 as r512
    root = root or DATA_ROOT
    saved = r512.PROMOTED
    r512.PROMOTED = os.path.join(root, PATHS["promoted"])
    try:
        route = r512.primary_routing(tree)
        snap = r512.snapshot_id(tree)
    finally:
        r512.PROMOTED = saved
    con = ro.open_ro(os.path.join(root, PATHS["snapshots"]))
    g = json.loads(con.execute("SELECT graph FROM snapshots WHERE id=?", (snap,)).fetchone()[0])
    con.close()
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())
    nodes = {n["id"]: n for n in lst}
    return route, r512.anchor_fn(nodes), snap


class Board:
    """A judged board routed to anchors: by[anchor] = list of (a, b, q, w) exactly as systematic_budget.build()
    builds it (valid rows, cache order, routed questions only); votes[anchor] = aligned (vote1, vote2_raw)."""

    def __init__(self, rows, route, anchor_of, models, keytab, label):
        self.label = label
        self.models = list(models)
        self.by = defaultdict(list); self.votes = defaultdict(list)
        self.n_valid = 0
        for a, b, q, w, inv, v1, v2 in rows:
            if inv:
                continue
            self.n_valid += 1
            if q in route:
                anc = anchor_of(route[q])
                self.by[anc].append((a, b, q, w))
                self.votes[anc].append((v1, v2))
        self.K, self.P, self.L = keytab.K, keytab.P, keytab.L

    def restrict(self, models=None, max_per_pair=None, rng=None, label=None):
        """A sub-board: rows among `models` only, and at most max_per_pair rows per (anchor, unordered pair), kept by a
        seeded random choice. Returns a new Board sharing K / P / L."""
        nb = Board.__new__(Board)
        nb.label = label or self.label; nb.models = sorted(models) if models else list(self.models)
        nb.by = defaultdict(list); nb.votes = defaultdict(list); nb.n_valid = 0
        nb.K, nb.P, nb.L = self.K, self.P, self.L
        keep = set(nb.models)
        for anc in sorted(self.by):
            cells = defaultdict(list)
            for k, r in enumerate(self.by[anc]):
                if r[0] in keep and r[1] in keep:
                    cells[tuple(sorted((r[0], r[1])))].append(k)
            take = []
            for key in sorted(cells):
                ks = cells[key]
                if max_per_pair is not None and len(ks) > max_per_pair:
                    ks = sorted(rng.sample(ks, max_per_pair))
                take.extend(ks)
            for k in sorted(take):
                nb.by[anc].append(self.by[anc][k]); nb.votes[anc].append(self.votes[anc][k]); nb.n_valid += 1
        return nb


# ----------------------------------------------------------------------------------------------- edge builders
def edges_exact(board, B=300, seed=42, floor=200, streams=None):
    """systematic_budget.build()'s per-anchor loop, line for line, on the read-only board."""
    import judge_free_tests as jf
    models = board.models
    K, P = board.K, board.P
    by = board.by
    rng = (streams.of_record("%s/edges_exact/build()-Random(%d)" % (board.label, seed), seed) if streams is not None
           else random.Random(seed))
    anchor_qs = {}
    edges = []
    for anc in sorted(by):
        rs = by[anc]
        if len(rs) < floor:
            continue
        qs = sorted({q for _, _, q, _ in rs})
        anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        for _ in range(B):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                        for a, b, _, w in sub], models))
            WITNESS["edges_exact.boards"] += 1
        la = {}
        for m in models:
            v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
            if v:
                la[m] = sum(v) / len(v)
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la:
                    continue
                gap = abs(la[a] - la[b])
                if gap == 0:
                    continue
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                both = [q for q in qs if P[q].get(a) and P[q].get(b)]
                if not both:
                    continue
                agree = sum(1 for q in both if P[q][a] == P[q][b]) / len(both)
                edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=len(both)))
                WITNESS["edges_exact.edges"] += 1
    return edges, anchor_qs


def canonical_edge_table(edges):
    """Byte-exact rendering: every field of every edge, floats by repr."""
    lines = ["anchor\ta\tb\tp\tm\ts\tright\tagree\tgap\tn"]
    for e in edges:
        lines.append("\t".join([e["anchor"], e["a"], e["b"], repr(e["p"]), repr(e["m"]), repr(e["s"]),
                                str(bool(e["right"])), repr(e["agree"]), repr(e["gap"]), str(e["n"])]))
    return "\n".join(lines) + "\n"


def mark_established(edges, K, anchor_qs, sb):
    for e in edges:
        p, b_, c_ = sb.mcnemar_edge(e, K, anchor_qs)
        e["est"] = p < 0.05
        e["mc_p"] = p
    return edges


def _wa(a, w):
    return 0.5 if w == "TIE" else (1.0 if w == a else 0.0)


def edges_fast(board, B, streams, tag, floor=200, per_order=False, length_offset=None, deff=False,
               tol=1e-10, keep_zero_gap=False, need_both=True):
    """The simulator's builder. Same edge fields as edges_exact; question draws from the named numpy stream
    '<tag>/<anchor>/qboot'. Extras when asked: m1 / m2 (per-order boards), m_len (length-offset board with coefficient
    length_offset per 1k characters), s_iid (match-level bootstrap on '<tag>/<anchor>/mboot') for DEFF."""
    models = board.models
    midx = {m: k for k, m in enumerate(models)}
    K, P, L = board.K, board.P, board.L
    edges = []; anchor_qs = {}
    for anc in sorted(board.by):
        rs = board.by[anc]
        if len(rs) < floor:
            continue
        qs = sorted({r[2] for r in rs})
        anchor_qs[anc] = qs
        qidx = {q: k for k, q in enumerate(qs)}
        Wq, Nq = bt.question_tensors([(a, b, q, _wa(a, w)) for a, b, q, w in rs], midx, qidx)
        counts = bt.boot_counts(streams.np("%s/%s/qboot" % (tag, anc)), len(qs), B)
        th = bt.boot_boards(Wq, Nq, counts, tol=tol)
        WITNESS["edges_fast.boards"] += B
        la = {}
        for m in models:
            v = [K[q][m] for q in qs if m in K.get(q, {})]
            if v:
                la[m] = sum(v) / len(v)
        pairs, meta = [], []
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                if a not in la or b not in la:
                    continue
                gap = abs(la[a] - la[b])
                if gap == 0 and not keep_zero_gap:
                    continue
                both = [q for q in qs if P.get(q, {}).get(a) and P.get(q, {}).get(b)]
                if need_both and not both:
                    continue
                agree = (sum(1 for q in both if P[q][a] == P[q][b]) / len(both)) if both else 0.0
                pairs.append((midx[a], midx[b])); meta.append((a, b, gap, agree, len(both)))
        if not pairs:
            continue
        p, mm, ss = bt.pair_moments(th, pairs)
        extra = {}
        if per_order or length_offset is not None:
            ri = np.array([midx[r[0]] for r in rs]); rj_ = np.array([midx[r[1]] for r in rs])
            rq = np.array([qidx[r[2] ] for r in rs])
            wts = counts[:, rq]
            if per_order:
                for o in (1, 2):
                    y = []; keep = []
                    for k, (v1, v2) in enumerate(board.votes[anc]):
                        v = v1 if o == 1 else v2
                        if v in ("Model A", "Model B", "TIE"):
                            # order 1 shows a first; order 2 shows b first ("Model A" = first-shown)
                            first_is_a = (o == 1)
                            y.append(0.5 if v == "TIE" else (1.0 if (v == "Model A") == first_is_a else 0.0)); keep.append(k)
                    keep = np.array(keep, dtype=int)
                    tho = bt.bt_offset_batch(ri[keep], rj_[keep], np.array(y), np.zeros(keep.size), wts[:, keep], len(models))
                    WITNESS["edges_fast.order_boards"] += B
                    extra["m%d" % o] = bt.pair_moments(tho, pairs)[1]
            if length_offset is not None:
                dl = np.array([((L.get(r[2], {}).get(r[0], np.nan) - L.get(r[2], {}).get(r[1], np.nan)) / 1000.0)
                               for r in rs])
                dl = np.where(np.isfinite(dl), dl, 0.0)
                y = np.array([_wa(r[0], r[3]) for r in rs])
                thl = bt.bt_offset_batch(ri, rj_, y, length_offset * dl, wts, len(models))
                WITNESS["edges_fast.length_boards"] += B
                extra["m_len"] = bt.pair_moments(thl, pairs)[1]
        if deff:
            n = len(rs)
            idx = streams.np("%s/%s/mboot" % (tag, anc)).integers(0, n, size=(B, n))
            mc = np.zeros((B, n)); np.add.at(mc, (np.repeat(np.arange(B), n), idx.ravel()), 1.0)
            Wm, Nm = bt.question_tensors([(a, b, k, _wa(a, w)) for k, (a, b, q, w) in enumerate(rs)], midx,
                                         {k: k for k in range(n)})
            thm = bt.boot_boards(Wm, Nm, mc, tol=tol)
            extra["s_iid"] = bt.pair_moments(thm, pairs)[2]
        for k, (a, b, gap, agree, n) in enumerate(meta):
            e = dict(anchor=anc, a=a, b=b, p=float(p[k]), m=float(mm[k]), s=float(ss[k]),
                     right=((p[k] > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=n, la=(la[a], la[b]))
            for key, arr in extra.items():
                e[key] = float(arr[k])
            edges.append(e)
            WITNESS["edges_fast.edges"] += 1
    return edges, anchor_qs
