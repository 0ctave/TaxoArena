"""v2_union_pool.py: the ENGINE's reserved-pool file of the v2 UNION pool pv2_1575de61bb20e977 (RP12 ARCH-V2-E-T, B2).

The union members of RP12's federated build are per-corpus constructions on the multi-corpus DB (multicorpus_cache_v1.db,
table corpus_questions, the corpus version mc6-2026-09-11 of the draw of record ARCH-V2-SPLIT-DRAW-2). Each loads ONE source
(LeaderboardCorpusSource.fetch: WHERE source = ?, question_id order, blank texts skipped; the engine id IS question_id,
namespaced id_offset + upstream_id). This script writes the one engine pool file all of them read (v2PoolFile), with the
namespaces of its ids (corpus_registry: source -> id_offset), so the engine checks one-to-one per loaded namespace
(V2EnginePool.scopedTo) and the union graft checks every member against it (V2EnginePool.checkUnionMembers). It reuses
v2_engine_pool.py (read_side = S1, pool_of = S2, write_once = S6, the file format) and adds nothing to the closure: the
Python CK-CLOSE-v2 draw is taken AS GIVEN.

CHECKS (each REFUSES and writes nothing): S1 the side export's LF rendering re-hashes to its table_sha; S2 the pool recomputed
for mc6-2026-09-11 equals --pool (FIRST printed line); S3 ROW BIJECTION with the sealed corpus_v2 union DB: its source_row pk
set for corpus_table 'corpus_questions' equals the engine rows' question_id set, and each row's item ("i:" + stem_key(text))
equals its source_row.item_id; S4 every row's item is in the export and tagged mc6-2026-09-11; S5 question_id == id_offset +
upstream_id for its source (the engine's own check) and every id lies in its source's namespace; S6 write-once.
Sentinels: corpus_questions carries no unlinked rows (every question_id is namespaced, >= 0), so sentinel_ids is empty and
counted; the EVAL items with no active response (the data layer's "sentinels") are EVAL rows here and reserved like any.

USAGE (zero calls; a POOL READER, never beside a construction; the run-operator's step after READY):
  python tools/analysis/v2_union_pool.py --selftest
  python tools/analysis/v2_union_pool.py --dry-run
  python tools/analysis/v2_union_pool.py              # writes experiment_configs/engine_pool_pv2_1575de61bb20e977.json
Defaults under TAXOARENA_DATA_ROOT: --source-db multicorpus_cache_v1.db, --corpus-db
data_v2/REG_ARCHV2-SPLIT-2_<seed>/corpus_v2_union_mc6.db; --side the committed export.

SELFTEST MUTANTS (run 2026-09-30 by a harness, one temporary edit at a time, reverted; V0 control survived): V1 GATE not reserved,
V2 S2 removed, V3 S3 item equality removed, V4 S4 corpus tag removed, V5 S5 offset check removed, V6 blank rows kept, V7
namespaces omitted, V8 --dry-run writes, V9 the pool computed for another corpus tag: 9 of 9 killed.
"""
import argparse
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import v2_engine_pool as EP  # noqa: E402
from data_v2 import common as C  # noqa: E402
from data_v2 import ro  # noqa: E402

DEFAULT_POOL = "pv2_1575de61bb20e977"
DEFAULT_CORPUS = "mc6-2026-09-11"
DEFAULT_SOURCE_DB = "multicorpus_cache_v1.db"
DEFAULT_CORPUS_DB = os.path.join("data_v2", EP.SPLIT_LABEL, "corpus_v2_union_mc6.db")
NAMESPACE_WIDTH = 1_000_000          # CorpusRegistry.NAMESPACE_WIDTH
ENGINE_SQL = "SELECT question_id, source, upstream_id, text FROM corpus_questions ORDER BY question_id ASC"


def refuse(msg):
    raise SystemExit("[UNION-POOL] REFUSED: " + msg)


def engine_rows(source_db):
    """[(question_id, source, text)] as LeaderboardCorpusSource.fetch loads them (blank texts dropped), and the offsets."""
    conn = ro.open_ro(source_db)
    try:
        offsets = {s: o for s, o in conn.execute("SELECT source, id_offset FROM corpus_registry")}
        rows = []
        for qid, src, up, text in conn.execute(ENGINE_SQL):
            if src not in offsets:
                refuse("S5: row %d has source %r, absent from corpus_registry" % (qid, src))
            if qid != offsets[src] + up:
                refuse("S5: row %d of %s: question_id != id_offset %d + upstream_id %d" % (qid, src, offsets[src], up))
            if not (offsets[src] <= qid < offsets[src] + NAMESPACE_WIDTH):
                refuse("S5: row %d lies outside the %s namespace" % (qid, src))
            if EP._kotlin_blank(text or ""):
                continue
            rows.append((qid, src, text))
        return rows, offsets
    finally:
        conn.close()


def corpus_source_rows(corpus_db):
    conn = ro.open_ro(corpus_db, require_sealed=True)
    try:
        return {pk: item for pk, item in conn.execute(
            "SELECT upstream_pk, item_id FROM source_row WHERE corpus_table = 'corpus_questions'")}
    finally:
        conn.close()


def build(side_path, source_db, corpus_db, pool, corpus, out=print):
    items, side_meta = EP.read_side(side_path)
    got, n_comp = EP.pool_of(items, corpus)
    out("[UNION-POOL] pool %s recomputed from the side export (%d EVAL components with a member in %s); expected %s"
        % (got, n_comp, corpus, pool))
    if got != pool:
        refuse("S2: the side export's %s pool is %s, not %s" % (corpus, got, pool))
    rows, offsets = engine_rows(source_db)
    src = corpus_source_rows(corpus_db)
    keys = C.KeyCache()
    row_item = {qid: "i:" + keys.stem(t) for qid, _s, t in rows}
    if set(row_item) != set(src):
        refuse("S3: engine rows %d vs corpus_v2 source_rows %d (only engine: %s; only corpus: %s)"
               % (len(row_item), len(src), sorted(set(row_item) - set(src))[:5], sorted(set(src) - set(row_item))[:5]))
    bad = sorted(q for q in row_item if src[q] != row_item[q])
    if bad:
        refuse("S3: %d engine row(s) key to another item than their source_row (first %d)" % (len(bad), bad[0]))
    out("[UNION-POOL] S3 row bijection: %d engine rows == %d corpus_v2 source_rows (corpus_questions), item per row equal"
        % (len(row_item), len(src)))
    by_side = {s: set() for s in EP.SIDES}
    per_src = {}
    for qid, s_, _t in rows:
        it = row_item[qid]
        if it not in items:
            refuse("S4: engine row %d (%s) has item %s, absent from the side export" % (qid, s_, it))
        comp, side, cs = items[it]
        if corpus not in cs:
            refuse("S4: engine row %d (%s) item %s is not tagged %s" % (qid, s_, it, corpus))
        by_side[side].add(qid)
        per_src.setdefault(s_, {"EVAL": 0, "GATE": 0, "TRAIN": 0})[side] += 1
    reserved = by_side["EVAL"] | by_side["GATE"]
    counts = {"rows": len(rows), "eval": len(by_side["EVAL"]), "gate": len(by_side["GATE"]), "train": len(by_side["TRAIN"]),
              "reserved": len(reserved), "sentinels_reserved": 0, "sentinels_train": 0,
              "global_reserved_items": sum(1 for (_c, s, _cs) in items.values() if s != "TRAIN"), "per_source": per_src}
    out("[UNION-POOL] ids: eval %(eval)d, gate %(gate)d, reserved %(reserved)d, train %(train)d; rows %(rows)d; global reserved"
        " items (all corpora) %(global_reserved_items)d" % counts)
    for s_ in sorted(per_src):
        out("[UNION-POOL]   %-10s namespace %8d: EVAL %d, GATE %d, TRAIN %d" % (s_, offsets[s_], per_src[s_]["EVAL"],
                                                                            per_src[s_]["GATE"], per_src[s_]["TRAIN"]))
    return {"format": EP.FORMAT, "rule": EP.RULE, "pool_id": pool, "corpus": corpus, "side_export": side_meta,
            "namespaces": {s_: offsets[s_] for s_ in sorted(per_src)},
            "engine_rows": {"sql": ENGINE_SQL, "source_db_sha256": ro.file_sha256(source_db),
                            "corpus_db_sha256": ro.file_sha256(corpus_db)},
            "generator": {"path": "tools/analysis/v2_union_pool.py", "blob": ro.git_blob_lf(os.path.abspath(__file__))},
            "counts": counts, "eval_ids": sorted(by_side["EVAL"]), "gate_ids": sorted(by_side["GATE"]),
            "train_ids": sorted(by_side["TRAIN"]), "sentinel_ids": []}


def main(argv=None, out=print):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=DEFAULT_POOL)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--side"); ap.add_argument("--source-db"); ap.add_argument("--corpus-db"); ap.add_argument("--out")
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    side = a.side or os.path.join(ROOT, EP.DEFAULT_SIDE)
    source_db = a.source_db or os.path.join(C.DATA_ROOT, DEFAULT_SOURCE_DB)
    corpus_db = a.corpus_db or os.path.join(C.DATA_ROOT, DEFAULT_CORPUS_DB)
    dest = a.out or os.path.join(ROOT, EP.default_out(a.pool))
    doc = build(side, source_db, corpus_db, a.pool, a.corpus, out=out)
    if a.dry_run:
        out("[UNION-POOL] DRY RUN: every check passed; nothing written (would write %s)" % dest)
        return 0
    EP.write_once(doc, dest)
    out("[UNION-POOL] wrote %s (write-once)" % dest)
    return 0


# ── selftest ────────────────────────────────────────────────────────────────────────────────────────────────────────
OFFSETS = {"MMLU_PRO": 0, "BBH": 1000000, "MATH": 2000000}
FX_ROWS = [  # (question_id, source, upstream_id, text, side, tag)
    (70, "MMLU_PRO", 70, "Union mmlu one", "EVAL", "mc6-2026-09-11,mmlu-pro-v2"),
    (71, "MMLU_PRO", 71, "Union mmlu two", "TRAIN", "mc6-2026-09-11,mmlu-pro-v2"),
    (1000001, "BBH", 1, "Bbh alpha", "EVAL", "mc6-2026-09-11"),
    (1000002, "BBH", 2, "Bbh beta", "GATE", "mc6-2026-09-11"),
    (1000003, "BBH", 3, "Bbh gamma", "TRAIN", "mc6-2026-09-11"),
    (1000004, "BBH", 4, "  ", None, None),
    (2000005, "MATH", 5, "Math delta", "TRAIN", "mc6-2026-09-11"),
    (2000006, "MATH", 6, "Math epsilon", "EVAL", "mc6-2026-09-11"),
]


def _fixture(tmp, override_item=None, retag=None, drop_item=None, bad_offset=False):
    ss = C.split_side
    src = os.path.join(tmp, "mc.db")
    c = ro.create_new(src)
    c.execute("CREATE TABLE corpus_registry (source TEXT, table_name TEXT, id_offset INTEGER, verifier TEXT)")
    for s, o in OFFSETS.items():
        c.execute("INSERT INTO corpus_registry VALUES (?,?,?,?)", (s, "corpus_questions", o, "x"))
    c.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT, upstream_id INTEGER, text TEXT)")
    for q, s, up, t, _sd, _tg in FX_ROWS:
        c.execute("INSERT INTO corpus_questions VALUES (?,?,?,?)", (q, s, up + (1 if bad_offset and q == 2000006 else 0), t))
    c.commit(); c.close()
    cdb = os.path.join(tmp, "corpus.db")
    c = ro.create_new(cdb)
    c.execute("CREATE TABLE source_row (source_row_id TEXT PRIMARY KEY, corpus_table TEXT, upstream_pk INTEGER, item_id TEXT)")
    for q, s, up, t, sd, tg in FX_ROWS:
        if sd is None:
            continue
        it = override_item if (override_item and q == 71) else "i:" + ss.stem_key(t)
        c.execute("INSERT INTO source_row VALUES (?,?,?,?)", ("r:%d" % q, "corpus_questions", q, it))
    ro.seal(c, cdb, "selftest")
    rows = []
    for q, s, up, t, sd, tg in FX_ROWS:
        if sd is None or q == drop_item:
            continue
        k = ss.stem_key(t)
        rows.append(("i:" + k, "c:" + k, sd, s, "d", (retag or {}).get(q, tg)))
    k = ss.stem_key("A foreign mmlu-only eval item")
    rows.append(("i:" + k, "c:" + k, "EVAL", "MMLU_PRO", "law", "mmlu-pro-v2"))
    rows.sort(key=lambda r: r[0])
    side = os.path.join(tmp, "side.tsv")
    from data_v2 import split as S
    with open(side, "w", encoding="utf-8", newline="\n") as f:
        f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (S.SIDE_EXPORT_FORMAT, S._side_rows_sha(rows), len(rows), "0" * 64))
        f.write("\t".join(S.SIDE_COLS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    comps = sorted({r[1] for r in rows if r[2] == "EVAL" and DEFAULT_CORPUS in r[5].split(",")})
    return side, src, cdb, S.pool_id(comps, dev=False)


def selftest():
    import io, contextlib, shutil
    fails, ran = [], []

    def case(name, fn):
        ran.append(name)
        tmp = tempfile.mkdtemp(prefix="v2union_")
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

    def run(argv):
        buf = io.StringIO()
        code, err = None, None
        with contextlib.redirect_stdout(buf):
            try:
                code = main(argv)
            except SystemExit as e:
                err = str(e)
        return code, err, buf.getvalue()

    def args(fx, dest, extra=()):
        return ["--side", fx[0], "--source-db", fx[1], "--corpus-db", fx[2], "--pool", fx[3], "--out", dest] + list(extra)

    def accept(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "p.json")
        code, err, text = run(args(fx, dest))
        assert code == 0 and err is None, (err, text)
        assert text.splitlines()[0] == ("[UNION-POOL] pool %s recomputed from the side export (3 EVAL components with a member in"
                                         " mc6-2026-09-11); expected %s" % (fx[3], fx[3])), text
        d = json.load(open(dest))
        assert d["eval_ids"] == [70, 1000001, 2000006] and d["gate_ids"] == [1000002] and d["train_ids"] == [71, 1000003, 2000005], d
        assert d["namespaces"] == {"BBH": 1000000, "MATH": 2000000, "MMLU_PRO": 0} and d["sentinel_ids"] == []
        c = d["counts"]
        assert (c["rows"], c["reserved"], c["global_reserved_items"]) == (7, 4, 5), c
        assert c["per_source"]["BBH"] == {"EVAL": 1, "GATE": 1, "TRAIN": 1}, c
        assert "[UNION-POOL]   BBH        namespace  1000000: EVAL 1, GATE 1, TRAIN 1" in text, text

    def dry(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "p.json")
        code, err, text = run(args(fx, dest, ["--dry-run"]))
        assert code == 0 and not os.path.exists(dest) and "DRY RUN" in text.splitlines()[-1]

    def s2(tmp):
        fx = _fixture(tmp)
        _c, err, _t = run(args((fx[0], fx[1], fx[2], "pv2_1575de61bb20e977"), os.path.join(tmp, "p.json")))
        assert err == "[UNION-POOL] REFUSED: S2: the side export's mc6-2026-09-11 pool is %s, not pv2_1575de61bb20e977" % fx[3], err

    def s3(tmp):
        fx = _fixture(tmp, override_item="i:" + "0" * 64)
        _c, err, _t = run(args(fx, os.path.join(tmp, "p.json")))
        assert err == "[UNION-POOL] REFUSED: S3: 1 engine row(s) key to another item than their source_row (first 71)", err

    def s4(tmp):
        fx = _fixture(tmp, retag={1000003: "mmlu-pro-v2"})
        _c, err, _t = run(args(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[UNION-POOL] REFUSED: S4: engine row 1000003 (BBH) item") and err.endswith("is not tagged mc6-2026-09-11"), err
        os.makedirs(os.path.join(tmp, "b"))
        fx2 = _fixture(os.path.join(tmp, "b"), drop_item=2000005)
        _c, err2, _t = run(args(fx2, os.path.join(tmp, "p2.json")))
        assert err2 is not None and err2.startswith("[UNION-POOL] REFUSED: S4: engine row 2000005 (MATH) has item"), err2

    def s5(tmp):
        fx = _fixture(tmp, bad_offset=True)
        _c, err, _t = run(args(fx, os.path.join(tmp, "p.json")))
        assert err == "[UNION-POOL] REFUSED: S5: row 2000006 of MATH: question_id != id_offset 2000000 + upstream_id 7", err

    def s6(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "p.json")
        assert run(args(fx, dest))[0] == 0
        _c, err, _t = run(args(fx, dest))
        assert err is not None and err.endswith("exists; the engine pool file is write-once"), err

    def committed(tmp):
        items, meta = EP.read_side(os.path.join(ROOT, EP.DEFAULT_SIDE))
        assert EP.pool_of(items, DEFAULT_CORPUS) == (DEFAULT_POOL, 5642)
        assert sum(1 for (_c, s, cs) in items.values() if s == "EVAL" and DEFAULT_CORPUS in cs) == 6153

    for nm, fn in [("committed export reproduces pv2_1575de61bb20e977 (5,642 / 6,153)", committed),
                   ("accept: ids, namespaces, counts, first line", accept), ("dry-run writes nothing", dry),
                   ("S2 wrong pool", s2), ("S3 item mismatch", s3), ("S4 corpus tag and absent item", s4),
                   ("S5 namespace arithmetic", s5), ("S6 write-once", s6)]:
        case(nm, fn)
    print("[UNION-POOL] selftest: %d / %d passed" % (len(ran) - len(fails), len(ran)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
