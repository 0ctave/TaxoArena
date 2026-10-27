"""data_v2.views (M3): the physical separation of the split, and the ONLY entry points a v2 stage reads text through.

From the sealed corpus_v2 DBs and the sealed split DB, two derived DBs are materialised and sealed:
  gen_view.db   TRAIN + GATE only: item / variant / source_row / label / label_conflict / answer_class / item_subset /
                alias rows of TRAIN + GATE items, their legacy references and the verbatim ordered option lists their
                rows point to (options_ordered), their responses WITHOUT the model output body (response_lite), the
                model registry, the side / component rows of TRAIN + GATE, and eval_key_hash: the SALTED hash set
                sha256(salt US stem_key) of every EVAL item. NO EVAL TEXT AND NO EVAL ROW EXIST IN THE FILE. The build
                re-keys every text in the file (source_row.text, variant.stem, item.stem_key) and REFUSES (the file is
                left unsealed, so no opener accepts it) if one hash is in the EVAL set.
  eval_view.db  EVAL only: the same tables for EVAL items, responses WITH their output bodies (zlib), and aliases.
                The build refuses when an item in it is not EVAL.

THE OPENERS (data §2.3; SYNTHESIS Stage S):
  open_generation(stage)  admits ONLY construct / label / induce / policy_fit and opens ONLY a sealed file whose meta says
                          view_kind = gen (a renamed eval_view is refused by its own meta, not by its name);
  open_eval(stage)        admits ONLY judge / arena / route and opens ONLY a sealed view_kind = eval file.
  Every other stage, an unknown stage and the wrong file are REFUSED by raise SystemExit("[DATA-V2-VIEW] ..."). The path
  comes from the argument or from TAXOARENA_V2_GEN_VIEW / TAXOARENA_V2_EVAL_VIEW; expect_sha256 pins the file bytes
  (the run manifest's pin). Both open read-only (data_v2.ro.open_ro, require_sealed).
  assert_not_eval(gen_conn, texts, where) is the write-time content assert for a generation artefact (data §2.4): it keys
  each text with split_side.stem_key and REFUSES on any hit in the salted EVAL set.
  responses_sql(include_quarantined=False) is the default response filter: QUARANTINED models only on an explicit flag.
"""
import hashlib
import json
import os
from collections import Counter

from . import common as C
from . import ro

GENERATION_STAGES = ("construct", "label", "induce", "policy_fit")
EVAL_STAGES = ("judge", "arena", "route")
GEN_KIND, EVAL_KIND = "gen", "eval"
CORPUS_TABLES = ("item", "variant", "source_row", "alias", "label", "label_conflict", "answer_class", "item_subset",
                 "model_registry", "response", "quarantine_check", "options_ordered", "reference")
# NOT carried into any view: reference_unresolved (no variant, so no side) and the retired upstream flag table (ingest.py
# RETIRED_NAMES; this module never names it).


def _refuse(msg):
    raise SystemExit("[DATA-V2-VIEW] " + msg)


# ── openers ─────────────────────────────────────────────────────────────────────────────────

def _open(kind, stage, path, expect_sha256, env):
    admitted = GENERATION_STAGES if kind == GEN_KIND else EVAL_STAGES
    other = EVAL_STAGES if kind == GEN_KIND else GENERATION_STAGES
    fn = "open_generation" if kind == GEN_KIND else "open_eval"
    if stage in other:
        _refuse("%s(stage=%r) REFUSED: stage %r may open only the %s view" % (fn, stage, stage,
                                                                           "eval" if kind == GEN_KIND else "generation"))
    if stage not in admitted:
        _refuse("%s(stage=%r) REFUSED: unknown stage (admitted: %s)" % (fn, stage, ", ".join(admitted)))
    path = path or os.environ.get(env)
    if not path:
        _refuse("%s(stage=%r): no view path (pass it or set %s)" % (fn, stage, env))
    conn = ro.open_ro(path, expect_sha256=expect_sha256, require_sealed=True)
    row = conn.execute("SELECT value FROM meta WHERE key='view_kind'").fetchone()
    if row is None or row[0] != kind:
        conn.close()
        _refuse("%s(stage=%r) REFUSED: %s is a %r view, not %r" % (fn, stage, path, row[0] if row else None, kind))
    return conn


def open_generation(stage, path=None, expect_sha256=None):
    return _open(GEN_KIND, stage, path, expect_sha256, "TAXOARENA_V2_GEN_VIEW")


def open_eval(stage, path=None, expect_sha256=None):
    return _open(EVAL_KIND, stage, path, expect_sha256, "TAXOARENA_V2_EVAL_VIEW")


def _salted(salt, stem_key):
    return hashlib.sha256((salt + C.US + stem_key).encode("utf-8")).hexdigest()


def assert_not_eval(gen_conn, texts, where=""):
    """REFUSE a generation artefact any of whose texts has an EVAL stem_key (the salted set of gen_view)."""
    salt = gen_conn.execute("SELECT value FROM meta WHERE key='eval_key_salt'").fetchone()[0]
    keys = C.KeyCache()
    hits = []
    for t in texts:
        h = _salted(salt, keys.stem(t))
        if gen_conn.execute("SELECT 1 FROM eval_key_hash WHERE h=?", (h,)).fetchone() is not None:
            hits.append(t[:60])
    if hits:
        raise SystemExit("[DATA-V2-VIEW] assert_not_eval%s: REFUSED, %d text(s) are EVAL content (e.g. %r)"
                         % ((" " + where) if where else "", len(hits), hits[:2]))
    return 0


def responses_sql(include_quarantined=False, table="response"):
    base = ("SELECT r.* FROM %s r JOIN model_registry m ON m.corpus_version = r.corpus_version AND m.model = r.model" % table)
    return base if include_quarantined else base + " WHERE m.status = 'ACTIVE'"


# ── the build ───────────────────────────────────────────────────────────────────────────────

def _view_ddl(src, table, drop_cols=()):
    cols = src.execute('PRAGMA table_info("%s")' % table).fetchall()
    keep = [c for c in cols if c[1] not in drop_cols]
    pk = [c[1] for c in sorted(cols, key=lambda c: c[5]) if c[5] > 0]
    if not pk:
        pk = [c[1] for c in keep]
    defs = ", ".join('"%s" %s' % (c[1], c[2]) for c in keep)
    return ('CREATE TABLE IF NOT EXISTS "%s" (corpus_version TEXT NOT NULL, %s, PRIMARY KEY (corpus_version, %s))'
            ' WITHOUT ROWID' % (table, defs, ", ".join('"%s"' % p for p in pk)), [c[1] for c in keep])


ITEM_TABLES = ("item", "label", "label_conflict", "answer_class", "item_subset", "variant", "source_row", "response",
               "reference")
ALL_ROW_TABLES = ("model_registry", "quarantine_check")


def _rows(src, table, cols, keep, row_item, variant_item, keep_opts=frozenset()):
    """The rows of `table` whose item is on the admitted sides (keep: a set of item ids). The source is read-only
    (query_only), so the filter runs here, not in a temp table."""
    sel = 'SELECT %s FROM "%s"' % (", ".join('"%s"' % x for x in cols), table)
    if table in ITEM_TABLES:
        k = cols.index("item_id")
        for row in src.execute(sel):
            if row[k] in keep:
                yield row
    elif table == "alias":
        kk, kt = cols.index("target_kind"), cols.index("target_id")
        for row in src.execute(sel):
            m = row_item if row[kk] == "source_row" else variant_item if row[kk] == "variant" else None
            if m is None:
                _refuse("alias target kind %r has no filter" % (row[kk],))
            if m[row[kt]] in keep:
                yield row
    elif table == "options_ordered":
        # only the option lists a kept source row or response points to (an options list shared by an EVAL and a
        # TRAIN row appears in both views: it is answer-choice text, not a stem, and no stem key is derived from it)
        k = cols.index("options_ordered_sha")
        for row in src.execute(sel):
            if row[k] in keep_opts:
                yield row
    elif table in ALL_ROW_TABLES:
        yield from src.execute(sel)
    else:
        _refuse("no filter for table %s" % table)


def build_view(kind, corpus_paths, split_path, out_dir, out=print):
    if kind not in (GEN_KIND, EVAL_KIND):
        _refuse("unknown view kind %r" % kind)
    sides = ("TRAIN", "GATE") if kind == GEN_KIND else ("EVAL",)
    split_sha = ro.file_sha256(split_path)
    sp = ro.open_ro(split_path, require_sealed=True)
    smeta = dict(sp.execute("SELECT key, value FROM meta"))
    side_of = dict(sp.execute("SELECT item_id, side FROM side"))
    # CK-CLOSE-v2 U: the items the split excluded from its universe are in NO view (neither side); any other item without a
    # side is still refused
    has_u = sp.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='excluded_u'").fetchone() is not None
    excluded_u = {i for (i,) in sp.execute("SELECT item_id FROM excluded_u")} if has_u else set()
    n_skipped = Counter()
    label = smeta["of_record"]
    tag = "DEV" if label == C.OF_RECORD_DEV else "REG"
    out_path = os.path.join(out_dir, "%s_view_%s.db" % (kind, tag))
    out("[M3] building %s (%s; sides %s) from split %s" % (os.path.basename(out_path), label, "+".join(sides),
                                                        os.path.basename(split_path)))
    conn = ro.create_new(out_path)
    conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID")
    # split rows of the admitted sides only
    for t, sql in (("side", "SELECT * FROM side WHERE side IN (%s)" % ",".join("'%s'" % s for s in sides)),
                   ("component", "SELECT * FROM component WHERE side IN (%s)" % ",".join("'%s'" % s for s in sides)),
                   ("stratum", "SELECT * FROM stratum"), ("pool", "SELECT * FROM pool")):
        ddl = sp.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()[0]
        conn.execute(ddl.replace("REFERENCES component(component_id)", ""))
        rows = sp.execute(sql).fetchall()
        if rows:
            conn.executemany('INSERT INTO "%s" VALUES (%s)' % (t, ",".join("?" * len(rows[0]))), rows)
    eval_keys = [iid[2:] for iid, s in side_of.items() if s == "EVAL"]
    sp.close()
    salt = hashlib.sha256(("gen_view-eval-key-salt" + C.US + split_sha).encode("utf-8")).hexdigest()[:32]
    if kind == GEN_KIND:
        conn.execute("CREATE TABLE eval_key_hash (h TEXT PRIMARY KEY) WITHOUT ROWID")
        conn.executemany("INSERT INTO eval_key_hash VALUES (?)", sorted((_salted(salt, k),) for k in eval_keys))
    corpora = []
    for path in corpus_paths:
        csha = ro.file_sha256(path)
        src = ro.open_ro(path, require_sealed=True)
        cmeta = dict(src.execute("SELECT key, value FROM meta"))
        cv = cmeta["corpus_version"]
        corpora.append({"corpus_version": cv, "path": os.path.basename(path), "sha256_bytes": csha})
        keep = set()
        for (iid,) in src.execute("SELECT item_id FROM item"):
            s = side_of.get(iid)
            if s is None:
                if iid in excluded_u:
                    n_skipped[cv] += 1
                    continue
                _refuse("item %s of %s has no side in the split and is not U-excluded" % (iid, cv))
            if s in sides:
                keep.add(iid)
        row_item = dict(src.execute("SELECT source_row_id, item_id FROM source_row"))
        variant_item = dict(src.execute("SELECT variant_id, item_id FROM variant"))
        keep_opts = {sha for sha, iid in src.execute("SELECT options_ordered_sha, item_id FROM source_row UNION ALL"
                                                      " SELECT options_ordered_sha, item_id FROM response") if iid in keep}
        n_by = {}
        for t in CORPUS_TABLES:
            drop = ("output_zlib",) if (kind == GEN_KIND and t == "response") else ()
            vt = "response_lite" if (kind == GEN_KIND and t == "response") else t
            ddl, cols = _view_ddl(src, t, drop)
            conn.execute(ddl.replace('"%s"' % t, '"%s"' % vt, 1))
            n = 0
            for row in _rows(src, t, cols, keep, row_item, variant_item, keep_opts):
                conn.execute('INSERT INTO "%s" VALUES (%s)' % (vt, ",".join("?" * (len(row) + 1))), (cv,) + tuple(row))
                n += 1
            n_by[vt] = n
        src.close()
        out("[M3]   %s: %s; U-excluded items left out of both views: %d" % (cv, ", ".join("%s %d" % kv for kv in n_by.items()),
                                                                           n_skipped[cv]))
    conn.commit()
    # the content check: every text in the file is re-keyed
    keys = C.KeyCache()
    ev = set(eval_keys)
    hits = 0
    n_checked = 0
    for (t,) in conn.execute("SELECT text FROM source_row UNION ALL SELECT stem FROM variant"):
        n_checked += 1
        k = keys.stem(t)
        if kind == GEN_KIND:
            hits += conn.execute("SELECT 1 FROM eval_key_hash WHERE h=?", (_salted(salt, k),)).fetchone() is not None
        else:
            hits += k not in ev
    for (sk,) in conn.execute("SELECT stem_key FROM item"):
        n_checked += 1
        hits += (sk in ev) if kind == GEN_KIND else (sk not in ev)
    what = "EVAL content in the generation view" if kind == GEN_KIND else "non-EVAL content in the eval view"
    out("[M3]   content check: %d texts / keys re-keyed, %d %s (must be 0)" % (n_checked, hits, what))
    if hits:
        conn.close()
        _refuse("%s: %d hit(s) of %s; the file is left UNSEALED and no opener accepts it" % (out_path, hits, what))
    meta = {"view_kind": kind, "of_record": label, "seed": smeta["seed"], "sides": ",".join(sides),
            "split_db": os.path.basename(split_path), "split_sha256_bytes": split_sha, "rule": smeta["rule"],
            "pools": smeta["pools"], "corpora": json.dumps(corpora, sort_keys=True),
            "views_blob": ro.git_blob_lf(os.path.abspath(__file__)), "content_check": "%d checked, 0 hits" % n_checked}
    if kind == GEN_KIND:
        meta["eval_key_salt"] = salt
        meta["eval_key_hash_rule"] = "sha256(salt U+001F split_side.stem_key) over every EVAL item"
        meta["eval_key_count"] = str(len(eval_keys))
    for k in sorted(meta):
        conn.execute("INSERT INTO meta VALUES (?,?)", (k, str(meta[k])))
    conn.commit()
    sealed = ro.seal(conn, out_path, "%s_view %s" % (kind, label))
    out("[M3] SEALED %s sha256-bytes %s" % (os.path.basename(out_path), sealed["sha256_bytes"]))
    return {"path": out_path, "kind": "%s_view" % kind, "of_record": label, "content_check": meta["content_check"], **sealed}
