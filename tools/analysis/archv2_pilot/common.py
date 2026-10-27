"""archv2_pilot.common: the split of record, read through data_v2's sealed eval_view (read-only), and the shared guards.

THE SPLIT OF RECORD (ARCH-V2-SPLIT-DRAW-1, b51eb71; R4 MET fa8e268): data_v2/REG_ARCHV2-SPLIT-1_<sha>/eval_view_REG.db,
sha256-bytes 7c284b15... (manifest data_v2/manifests/REG_ARCHV2-SPLIT-1_<sha>.json). Opened ONLY through
data_v2.views.open_eval(stage, path, expect_sha256) (mode=ro&immutable=1, query_only, sealed, view_kind = eval).

CORPUS VERSION IS ALWAYS NAMED (judge-design ruling relayed 2026-09-24): eval_view's item / variant / response / reference
rows are keyed by (corpus_version, ...) and 7,098 variants sit in both mmlu-pro-v2 and mc6. Every count and schedule here
joins `item` (or `response`, `reference`) ON corpus_version = the corpus of the pool, and asserts that the counted ids are
DISTINCT (a count without the filter double-counts; mutant "cv_filter_dropped" in the selftest).

ANCHOR OF AN ITEM: the split's stratum of the item (side.stratum_source / side.stratum_domain), which for the MMLU-Pro
pool is (MMLU_PRO, mmlu_pro.category); the anchor name is stratum_domain.strip().lower() (the normalisation of
archv2_arena.data.KeyTable's categories, so names match the simulator's strata); a pool item whose stratum source is not
MMLU_PRO, a normalisation collision, or an anchor count other than 14 is REFUSED.

[RE-PINNED 2026-09-24 to the NEW split of record, insertion only: ARCH-V2-SPLIT-DRAW-2 (draw 5a3e756, CK-CLOSE-v2,
Amendments 19 / 20; R4 MET e2623b4): data_v2/REG_ARCHV2-SPLIT-2_2929bd46.../eval_view_REG.db sha256-bytes e35b7518...,
pools pv2_41dbd3dbcd399df0 (mmlu-pro-v2: 3,400 components, 3,492 items) and pv2_1575de61bb20e977 (scope "all corpora +
mc6-2026-09-11"). The split-1 constants above (7c284b15..., pv2_6f78..., pv2_4cce...) are superseded and kept as
SPLIT1_* for disclosure. data_v2 at 093ab1e: the pool table carries n_items_by_scope (JSON {scope: n}) and a merged
scope ("A + B", merge_pool); pool_of reads either schema. U-excluded items are in NO view (views.build_view skips them), so
every count here, read from the view, already leaves them out; a record open also checks the view's meta seed.]

Guards raise SystemExit (python -O safe). MUTANT is a SELFTEST-ONLY switch (None in every real run; the CLIs print it
and refuse a record run when it is set).
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ANALYSIS))
if ANALYSIS not in sys.path:
    sys.path.insert(0, ANALYSIS)

from data_v2 import common as dv2c  # noqa: E402
from data_v2 import ro as dv2ro  # noqa: E402
from data_v2 import views as dv2views  # noqa: E402
from archv2_arena import report  # noqa: E402

DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
SPLIT1_LABEL = "REG_ARCHV2-SPLIT-1_c03031568a0a9d827d834b075512b8e4dd095642"          # superseded (disclosure)
SPLIT1_EVAL_VIEW_SHA256 = "7c284b15c45aa381654b5d175549fbac49269e0f4eed00c24e26990220650fb1"
SPLIT1_POOLS = ("pv2_6f78aece2bf9a612", "pv2_4cce62591eb5a2cb")
SPLIT_LABEL = "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"
SPLIT_SEED = "ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2"
EVAL_VIEW_REL = os.path.join("data_v2", SPLIT_LABEL, "eval_view_REG.db")
EVAL_VIEW_SHA256 = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"
POOL_MMLU = "pv2_41dbd3dbcd399df0"
CV_MMLU = "mmlu-pro-v2"
POOL_UNION = "pv2_1575de61bb20e977"
CV_UNION = "mc6-2026-09-11"
MMLU_SOURCE = "MMLU_PRO"
N_ANCHORS = 14
FROZEN_INSTRUMENT_LF16 = "876d01413318bd7b"      # g22.instrument_lf16() of the 11 frozen files (the chain is live)
LETTERS = dv2c.LETTERS

MUTANT = None            # SELFTEST-ONLY: "cv_filter_dropped"


def refuse(msg):
    raise SystemExit("[ARCHV2-PILOT] " + msg)


need = report.need


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def default_view_path():
    return os.path.join(DATA_ROOT, EVAL_VIEW_REL)


def check_instrument():
    """The frozen instrument is imported read-only: its lf16 must be the chain's."""
    from archv2_arena import g22
    got = g22.instrument_lf16()
    if got != FROZEN_INSTRUMENT_LF16:
        refuse("the frozen G22 / G23 instrument is sha256-lf16 %s, not %s: its 11 files were changed; refused"
               % (got, FROZEN_INSTRUMENT_LF16))
    return got


def open_view(stage, path, expect_sha256, out=print):
    """The eval_view through data_v2.views.open_eval ONLY. expect_sha256 None is admitted only for a DEV fixture (the
    caller decides); the bytes' sha256 is always computed and printed."""
    sha = dv2ro.file_sha256(path)
    conn = dv2views.open_eval(stage, path, expect_sha256)
    meta = dict(conn.execute("SELECT key, value FROM meta"))
    if expect_sha256 is not None and expect_sha256 == EVAL_VIEW_SHA256 and meta.get("seed") != SPLIT_SEED:
        conn.close()
        refuse("the eval_view's meta seed %r is not the split of record's %r" % (meta.get("seed"), SPLIT_SEED))
    out("  eval_view %s | sha256-bytes %s%s | of_record %r | seed %r | split %s" % (
        path, sha, " (= the pinned sha)" if expect_sha256 == sha else " (NOT PINNED: DEV)", meta.get("of_record"),
        meta.get("seed"), meta.get("split_db")))
    return conn, sha, meta


def pool_of(conn, cv, expect_pool_id=None):
    """The eval_view's pool row whose scope NAMES the corpus version cv (exactly one; a merged scope is "A + B"); with
    expect_pool_id, its id must equal it. n_items is the cv's count: n_items_by_scope[cv] (data_v2 at 093ab1e), or the
    older single n_items column."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(pool)")]
    if "n_items_by_scope" in cols:
        rows = []
        for pid, scope, n_comp, by in conn.execute("SELECT pool_id, scope, n_components, n_items_by_scope FROM pool"):
            scopes = [x.strip() for x in str(scope).split(" + ")]
            if cv in scopes:
                d = json.loads(by)
                need(isinstance(d, dict) and cv in d, "pool %s: n_items_by_scope %r lacks %s" % (pid, by, cv))
                rows.append((pid, scope, n_comp, d[cv]))
    elif "n_items" in cols:
        rows = conn.execute("SELECT pool_id, scope, n_components, n_items FROM pool WHERE scope=?", (cv,)).fetchall()
    else:
        refuse("the eval_view's pool table has neither n_items_by_scope nor n_items: %s" % cols)
    if len(rows) != 1:
        refuse("eval_view carries %d pool rows whose scope names %r (exactly 1 required)" % (len(rows), cv))
    pid, scope, n_comp, n_items = rows[0]
    if expect_pool_id is not None and pid != expect_pool_id:
        refuse("the pool of %s is %s, not the pool of record %s" % (cv, pid, expect_pool_id))
    return {"pool_id": pid, "scope": scope, "n_components": int(n_comp), "n_items": int(n_items)}


def eval_items(conn, cv):
    """{item_id: (stratum_source, stratum_domain)} over the EVAL items OF THE CORPUS cv: side JOIN item ON corpus_version
    = cv. The ids are asserted distinct; each row's side is EVAL and its `corpora` names cv."""
    if MUTANT == "cv_filter_dropped":
        sql = ("SELECT s.item_id, s.stratum_source, s.stratum_domain, s.corpora, s.side FROM side s JOIN item i ON"
               " i.item_id = s.item_id")
        rows = conn.execute(sql).fetchall()
    else:
        sql = ("SELECT s.item_id, s.stratum_source, s.stratum_domain, s.corpora, s.side FROM side s JOIN item i ON"
               " i.item_id = s.item_id AND i.corpus_version = ?")
        rows = conn.execute(sql, (cv,)).fetchall()
    ids = [r[0] for r in rows]
    need(len(ids) == len(set(ids)), "eval_items(%s): %d rows but %d distinct item ids: a count over eval_view must name"
         " corpus_version (the judge-design ruling); refused" % (cv, len(ids), len(set(ids))))
    out = {}
    for iid, src, dom, corpora, side in rows:
        need(side == "EVAL", "eval_items: item %s has side %r in the eval view" % (iid, side))
        need(cv in str(corpora).split(","), "eval_items: item %s of %s does not name %s in side.corpora (%r)"
             % (iid, cv, cv, corpora))
        out[iid] = (src, dom)
    return out


def anchor_of_items(conn, cv, pool, source=MMLU_SOURCE, n_anchors=N_ANCHORS):
    """(item -> anchor, anchor -> EVAL item count, anchor -> raw domain) for the MMLU-Pro pool. REFUSES when the item
    count differs from the pool row's n_items, a stratum source is not MMLU_PRO, two raw domains normalise to one name,
    or the anchor count is not n_anchors."""
    items = eval_items(conn, cv)
    need(len(items) == pool["n_items"], "the EVAL items of %s counted by item_id (%d) differ from the pool row %s's"
         " n_items %d" % (cv, len(items), pool["pool_id"], pool["n_items"]))
    anchor_of, raw = {}, {}
    for iid, (src, dom) in items.items():
        need(src == source, "item %s of the %s pool has stratum source %r, not %s" % (iid, cv, src, source))
        a = str(dom).strip().lower()
        if a in raw and raw[a] != dom:
            refuse("two raw anchor names %r and %r normalise to %r" % (raw[a], dom, a))
        raw[a] = dom
        anchor_of[iid] = a
    counts = {}
    for a in anchor_of.values():
        counts[a] = counts.get(a, 0) + 1
    need(len(counts) == n_anchors, "the %s pool has %d anchors, not %d: %s" % (cv, len(counts), n_anchors, sorted(counts)))
    return anchor_of, counts, raw


def judgeable_items(conn, cv):
    """Items of cv with at least one ACTIVE-model response in the eval view (the corpus version named)."""
    rows = conn.execute("SELECT DISTINCT r.item_id FROM response r JOIN model_registry m ON m.corpus_version ="
                        " r.corpus_version AND m.model = r.model WHERE m.status = 'ACTIVE' AND r.corpus_version = ?",
                        (cv,)).fetchall()
    ids = [r[0] for r in rows]
    need(len(ids) == len(set(ids)), "judgeable_items: ids not distinct")
    return set(ids)


def counts_digest(counts):
    """sha256 over "name TAB count LF" lines sorted by name (hash kind sha256-text)."""
    return sha256_text("".join("%s\t%d\n" % (k, int(v)) for k, v in sorted(counts.items())))


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=True) + "\n"


def write_once_json(path, obj):
    """Write-once (mode "x" via report.write_once); returns sha256 of the bytes written."""
    txt = canonical_json(obj)
    report.write_once(path, txt)
    return sha256_text(txt)


def code_pins(rel_paths):
    """{rel: "blob:<git blob of LF> sha256-lf16:<16 hex>"} (hash kinds named, CONTEXT rule 8)."""
    out = {}
    for rel in rel_paths:
        p = os.path.join(ANALYSIS, *rel.split("/"))
        out[rel] = "blob:%s sha256-lf16:%s" % (dv2ro.git_blob_lf(p), dv2ro.sha256_lf16(p))
    return out


PACKAGE_FILES = ("archv2_pilot/__init__.py", "archv2_pilot/common.py", "archv2_pilot/stage1.py", "archv2_pilot/supply.py",
                 "archv2_pilot/pilot.py", "archv2_pilot/analysis.py", "archv2_pilot/accounting.py",
                 "archv2_pilot/outcome.py")


def package_lf16():
    h = hashlib.sha256()
    for rel in PACKAGE_FILES:
        h.update(rel.encode("utf-8") + b"\0")
        with open(os.path.join(ANALYSIS, *rel.split("/")), "rb") as f:
            h.update(f.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]
