"""v2_engine_pool.py: the ENGINE's reserved-pool file of a v2 pool (RP12 ARCH-V2-E-T, engineering prerequisite 1).

WHAT IT IS. The construction engine (Kotlin) takes the Python v2 closure AS GIVEN (the orchestrator's scope ruling of
2026-09-29, the fast route: CK-CLOSE-v2 is NOT re-implemented in Kotlin). This script turns the draw of record's committed
side export (data_v2/manifests/REG_ARCHV2-SPLIT-2_..._side.tsv, split ARCH-V2-SPLIT-DRAW-2, KNOWLEDGE.md section 1) into the
engine's id space: every row the engine loads from mmlu_pro (the engine's own loadFromDb SQL, mirrored below, sentinel
ids included) gets the side of its item ("i:" + split_side.stem_key(question)). The file RESERVES EVAL, GATE and the
sentinel rows among them (negative engine ids, UNLINKED_QUERY_ID_BASE - rowid, listed explicitly: CK-CLOSE condition 1)
and lists TRAIN, so the engine can check TRAIN one-to-one (V2EnginePool.kt / MMLUDatasetFetcher.splitByV2Pool). It is an
engineering item, not a registered test (queue ARCH-V2-E-T, "an engineering item: its own READY"); it reads no verdict and
posts no call.

CHECKS (each REFUSES, SystemExit, and writes nothing):
  S1  the side export's LF rendering re-hashes from its TEXT to its header's table_sha (verify_side_export's rules and
      data_v2.split._side_rows_sha, reused; the pin is sha256 of the LF rendering, sha256_lf);
  S2  the pool id recomputed from the export (pv2_ + sha256 of the sorted EVAL component ids with a member in --corpus,
      data_v2.split.pool_id, reused) equals --pool; this is the FIRST printed line (the pool_guard convention);
  S3  ROW BIJECTION: the engine rows' mmlu_pro.id set equals the sealed corpus_v2 DB's source_row upstream_pk set for
      corpus_table 'mmlu_pro', and each row's item ("i:" + stem_key(question)) equals its source_row.item_id;
  S4  every engine row's item is in the side export and carries --corpus in its corpora column;
  S5  one engine id has one side (a LEFT JOIN duplicate or a shared link id with two sides is refused);
  S6  the output path does not exist (outcome files are write-once, mode "x").

USAGE (zero calls; a POOL READER: never beside a construction or a site null, CONTEXT rule 7; the run-operator's slot):
  python tools/analysis/v2_engine_pool.py --selftest
  python tools/analysis/v2_engine_pool.py --dry-run      # every check, the counts, writes nothing
  python tools/analysis/v2_engine_pool.py               # writes experiment_configs/engine_pool_pv2_41dbd3dbcd399df0.json
Defaults: --pool pv2_41dbd3dbcd399df0 --corpus mmlu-pro-v2 --source-db mmlu_pro_dataset_cache_v2.db --corpus-db
data_v2/REG_ARCHV2-SPLIT-2_<seed>/corpus_v2_mmlu_pro_v2.db --side data_v2/manifests/REG_ARCHV2-SPLIT-2_<seed>_side.tsv,
DB paths under TAXOARENA_DATA_ROOT (default: this checkout). Both DBs are opened through data_v2.ro.open_ro
(mode=ro&immutable=1 after the non-empty -wal / -journal refusal); the corpus DB must be sealed.

THE ENGINE ID RULE (MMLUDatasetFetcher.loadFromDb + formatData, mirrored; a change there is a change here):
  SELECT m.id, m.question, ..., l.question_id FROM mmlu_pro m LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id
  ORDER BY m.id; id = l.question_id when it is non-NULL and > 0, else UNLINKED_QUERY_ID_BASE (-1,000,000) - m.id; rows
  whose question is blank are dropped (formatData's isNotBlank).

SELFTEST MUTANTS (run 2026-09-29 by a harness on this file, one temporary edit at a time, reverted; P0 is the harness
control and must survive):
  mutant                                             result
  P0  control (a comment appended)                   survived (the harness reports a live mutant)
  M1  GATE not reserved (reserved = EVAL only)       killed: accept path (counts / gate ids)
  M2  sentinel ids dropped                           killed: accept path (sentinel list [-1000009])
  M3  pool id over ALL EVAL components               killed: committed export (pv2_41dbd3dbcd399df0) and accept path (S2)
  M4  S3 item equality removed                       killed: S3 item-mismatch refusal
  M5  S4 corpora filter removed                      killed: S4 foreign-corpus refusal
  M6  S5 removed (last side wins)                    killed: S5 two-sides refusal
  M7  output opened "w" (S6 check kept)              SURVIVED: equivalent while the S6 existence check stands (M7b)
  M7b S6 existence check removed                     killed: S6 write-once case (mode "x" raises; value assert fails)
  M8  unlinked id = m.id (no sentinel base)          killed: accept path (eval ids [9, ...])
  M9  blank-question rows kept                       killed: accept path and dry-run (the blank stem refuses)
  M10 --dry-run writes the file                      killed: dry-run case
  M11 S2 comparison removed                          killed: S2 wrong-pool refusal
  M12 S1 sha comparison removed                      killed: S1 tampered-export refusal (the message names S1)
  M13 CRLF not normalised                            killed: committed export (the worktree renders it CRLF)
  M14 global reserved count over EVAL only           killed: accept path (global reserved items 8)
14 of 15 non-control mutants killed; M7 is equivalent under M7b's check.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from data_v2 import common as C  # noqa: E402  (loads split_side / content_closure by their pinned blobs)
from data_v2 import ro  # noqa: E402
from data_v2 import split as S  # noqa: E402

FORMAT = "taxoarena-engine-pool-v2"
RULE = "CK-CLOSE-v2"
UNLINKED_QUERY_ID_BASE = -1_000_000
DEFAULT_POOL = "pv2_41dbd3dbcd399df0"
DEFAULT_CORPUS = "mmlu-pro-v2"
SPLIT_LABEL = "REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"
DEFAULT_SIDE = os.path.join("data_v2", "manifests", SPLIT_LABEL + "_side.tsv")
DEFAULT_CORPUS_DB = os.path.join("data_v2", SPLIT_LABEL, "corpus_v2_mmlu_pro_v2.db")
DEFAULT_SOURCE_DB = "mmlu_pro_dataset_cache_v2.db"
ENGINE_SQL = ("SELECT m.id, m.question, m.category, l.question_id FROM mmlu_pro m"
              " LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id ORDER BY m.id ASC")
SIDES = ("EVAL", "GATE", "TRAIN")


def refuse(msg):
    raise SystemExit("[ENGINE-POOL] REFUSED: " + msg)


def default_out(pool):
    return os.path.join("experiment_configs", "engine_pool_%s.json" % pool)


def _kotlin_blank(s):
    """Kotlin's CharSequence.isBlank: empty or every char whitespace (Character.isWhitespace; str.isspace covers it)."""
    return s is None or s == "" or s.isspace()


def read_side(path):
    """S1: verify the export's LF RENDERING from its text, then {item_id: (component_id, side, corpora set)} and the header.
    The rules are data_v2.split.verify_side_export's (format line, column header, item_id order, S._side_rows_sha against
    the header's table_sha and row count), applied to the LF rendering: a Windows checkout (core.autocrlf) renders the
    committed LF blob with CRLF, which verify_side_export refuses as "not LF-only". The pin is sha256 of the LF rendering
    (sha256_lf), never of the working-tree bytes."""
    with open(path, "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    if b"\r" in data:
        refuse("S1: side export %s carries a bare CR" % path)
    lines = data.decode("utf-8").split("\n")
    if lines[-1] != "":
        refuse("S1: side export %s does not end with LF" % path)
    head = lines[0].split()
    if len(head) != 5 or head[1] != S.SIDE_EXPORT_FORMAT:
        refuse("S1: side export %s: bad header %r" % (path, lines[0]))
    hdr = dict(x.split("=", 1) for x in head[2:])
    if lines[1].split("\t") != list(S.SIDE_COLS):
        refuse("S1: side export %s: bad column header" % path)
    trows = [tuple(ln.split("\t")) for ln in lines[2:-1]]
    if any(len(r) != len(S.SIDE_COLS) for r in trows) or trows != sorted(trows, key=lambda r: r[0]):
        refuse("S1: side export %s: malformed or unordered rows" % path)
    table_sha, rows = S._side_rows_sha(trows), len(trows)
    if table_sha != hdr["table_sha"] or rows != int(hdr["rows"]):
        refuse("S1: side export %s: text sha %s / rows %d != header %s / %s" % (path, table_sha, rows, hdr["table_sha"],
                                                                                 hdr["rows"]))
    items = {}
    for ln in lines[2:-1]:
        item_id, comp, side, _src, _dom, corpora = ln.split("\t")
        if side not in SIDES:
            refuse("side export row %s has side %r" % (item_id, side))
        items[item_id] = (comp, side, frozenset(corpora.split(",")))
    ap_ = os.path.abspath(path)
    shown = os.path.relpath(ap_, ROOT) if os.path.normcase(ap_).startswith(os.path.normcase(ROOT) + os.sep) else ap_
    meta = {"path": shown.replace("\\", "/"), "sha256_lf": hashlib.sha256(data).hexdigest(), "table_sha": table_sha,
            "rows": rows, "split_sha256": hdr["split_sha256"]}
    return items, meta


def pool_of(items, corpus):
    comps = sorted({c for (c, s, cs) in items.values() if s == "EVAL" and corpus in cs})
    return S.pool_id(comps, dev=False), len(comps)


def engine_rows(source_db):
    """The engine's rows: [(local_id, engine_id, question, category)] in the engine's order, blank questions dropped."""
    conn = ro.open_ro(source_db)
    try:
        out = []
        for mid, q, cat, qid in conn.execute(ENGINE_SQL):
            eid = qid if (qid is not None and qid > 0) else UNLINKED_QUERY_ID_BASE - mid
            if _kotlin_blank(q):
                continue
            out.append((mid, eid, q, cat))
        return out
    finally:
        conn.close()


def corpus_source_rows(corpus_db):
    conn = ro.open_ro(corpus_db, require_sealed=True)
    try:
        return {pk: item for pk, item in conn.execute(
            "SELECT upstream_pk, item_id FROM source_row WHERE corpus_table = 'mmlu_pro'")}
    finally:
        conn.close()


def build(side_path, source_db, corpus_db, pool, corpus, out=print):
    items, side_meta = read_side(side_path)
    got, n_comp = pool_of(items, corpus)
    out("[ENGINE-POOL] pool %s recomputed from the side export (%d EVAL components with a member in %s); expected %s"
        % (got, n_comp, corpus, pool))
    if got != pool:
        refuse("S2: the side export's %s pool is %s, not %s" % (corpus, got, pool))
    out("[ENGINE-POOL] S1 side export %s: %d rows, table_sha %s (re-hashed from the text)"
        % (side_meta["path"], side_meta["rows"], side_meta["table_sha"]))
    rows = engine_rows(source_db)
    src = corpus_source_rows(corpus_db)
    keys = C.KeyCache()
    row_item = {}
    for mid, eid, q, cat in rows:
        row_item[mid] = "i:" + keys.stem(q)
    # S3: the row bijection (every engine row is one source_row of the ingest and vice versa, same item)
    engine_pks = set(row_item)
    src_nonblank = set(src)
    if engine_pks != src_nonblank:
        refuse("S3: engine rows %d vs corpus_v2 source_rows %d (only engine: %s; only corpus: %s)"
               % (len(engine_pks), len(src_nonblank), sorted(engine_pks - src_nonblank)[:5],
                  sorted(src_nonblank - engine_pks)[:5]))
    bad = sorted(pk for pk in engine_pks if src[pk] != row_item[pk])
    if bad:
        refuse("S3: %d engine row(s) key to another item than their source_row (first pk %s: %s vs %s)"
               % (len(bad), bad[0], row_item[bad[0]], src[bad[0]]))
    out("[ENGINE-POOL] S3 row bijection: %d engine rows == %d corpus_v2 source_rows (mmlu_pro), item per row equal"
        % (len(engine_pks), len(src_nonblank)))
    side_of_id = {}
    by_side = {s: set() for s in SIDES}
    for mid, eid, q, cat in rows:
        it = row_item[mid]
        if it not in items:
            refuse("S4: engine row %d (id %d) has item %s, absent from the side export" % (mid, eid, it))
        comp, side, cs = items[it]
        if corpus not in cs:
            refuse("S4: engine row %d (id %d) item %s is not tagged %s (corpora %s)" % (mid, eid, it, corpus, sorted(cs)))
        prev = side_of_id.get(eid)
        if prev is not None and prev != side:
            refuse("S5: engine id %d carries two sides (%s, %s)" % (eid, prev, side))
        side_of_id[eid] = side
        by_side[side].add(eid)
    reserved = by_side["EVAL"] | by_side["GATE"]
    sentinels = sorted(i for i in reserved if i < 0)
    global_reserved_items = sum(1 for (_c, s, _cs) in items.values() if s != "TRAIN")
    counts = {"rows": len(rows), "eval": len(by_side["EVAL"]), "gate": len(by_side["GATE"]),
              "train": len(by_side["TRAIN"]), "reserved": len(reserved), "sentinels_reserved": len(sentinels),
              "sentinels_train": sum(1 for i in by_side["TRAIN"] if i < 0),
              "global_reserved_items": global_reserved_items}
    out("[ENGINE-POOL] ids: eval %(eval)d, gate %(gate)d, reserved %(reserved)d (sentinels reserved %(sentinels_reserved)d),"
        " train %(train)d (sentinels train %(sentinels_train)d); rows %(rows)d; global reserved items (all corpora)"
        " %(global_reserved_items)d" % counts)
    doc = {"format": FORMAT, "rule": RULE, "pool_id": pool, "corpus": corpus, "side_export": side_meta,
           "engine_rows": {"sql": ENGINE_SQL, "unlinked_query_id_base": UNLINKED_QUERY_ID_BASE,
                           "source_db_sha256": ro.file_sha256(source_db),
                           "corpus_db_sha256": ro.file_sha256(corpus_db)},
           "generator": {"path": "tools/analysis/v2_engine_pool.py",
                         "blob": ro.git_blob_lf(os.path.abspath(__file__))},
           "counts": counts,
           "eval_ids": sorted(by_side["EVAL"]), "gate_ids": sorted(by_side["GATE"]),
           "train_ids": sorted(by_side["TRAIN"]), "sentinel_ids": sentinels}
    return doc


def write_once(doc, path):
    if os.path.exists(path):
        refuse("S6: %s exists; the engine pool file is write-once" % path)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pool", default=DEFAULT_POOL)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--side", default=None)
    ap.add_argument("--source-db", default=None)
    ap.add_argument("--corpus-db", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    data_root = C.DATA_ROOT
    side = a.side or os.path.join(ROOT, DEFAULT_SIDE)
    source_db = a.source_db or os.path.join(data_root, DEFAULT_SOURCE_DB)
    corpus_db = a.corpus_db or os.path.join(data_root, DEFAULT_CORPUS_DB)
    dest = a.out or os.path.join(ROOT, default_out(a.pool))
    doc = build(side, source_db, corpus_db, a.pool, a.corpus, out=out)
    if a.dry_run:
        out("[ENGINE-POOL] DRY RUN: every check passed; nothing written (would write %s)" % dest)
        return 0
    write_once(doc, dest)
    out("[ENGINE-POOL] wrote %s (write-once)" % dest)
    return 0


# ── selftest: fixture DBs in a temp dir; every deciding path executed through main() ─────────────────────────────────

def _fixture(tmp, *, foreign_eval=True, drop_side_item=None, retag=None, src_item_override=None, extra_link=None):
    """A 12-row mmlu_pro fixture (one blank row, one unlinked row), its sealed corpus_v2 source_row table, and a side
    export whose sides are chosen by hand. Returns (side_path, source_db, corpus_db, pool)."""
    split_side = C.split_side
    texts = {1: "Alpha question", 2: "Beta question", 3: "Gamma question", 4: "Delta question", 5: "Epsilon question",
             6: "Zeta question", 7: "Eta question", 8: "Theta question", 9: "Iota question", 10: "Kappa question",
             11: "   ", 12: "Lambda question"}
    links = {1: 501, 2: 502, 3: 503, 4: 504, 5: 505, 6: 506, 7: 507, 8: 508, 10: 510, 11: 511, 12: 512}  # 9 unlinked
    if extra_link:
        links.update(extra_link)
    side_by_row = {1: "EVAL", 2: "EVAL", 3: "GATE", 4: "TRAIN", 5: "TRAIN", 6: "TRAIN", 7: "EVAL", 8: "GATE",
                   9: "EVAL", 10: "TRAIN", 12: "TRAIN"}
    src = os.path.join(tmp, "src.db")
    c = ro.create_new(src)
    c.execute("CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY, question TEXT, category TEXT, cot_content TEXT,"
              " options TEXT, answer TEXT)")
    c.execute("CREATE TABLE eval_question_link (question_id INTEGER, mmlu_pro_row_id INTEGER)")
    for i, t in texts.items():
        c.execute("INSERT INTO mmlu_pro VALUES (?,?,?,?,?,?)", (i, t, "cat%d" % (i % 2), "", "[]", "A"))
    for i, q in links.items():
        c.execute("INSERT INTO eval_question_link VALUES (?,?)", (q, i))
    c.commit()
    c.close()
    cdb = os.path.join(tmp, "corpus.db")
    c = ro.create_new(cdb)
    c.execute("CREATE TABLE source_row (source_row_id TEXT PRIMARY KEY, corpus_table TEXT NOT NULL,"
              " upstream_pk INTEGER NOT NULL, item_id TEXT NOT NULL)")
    for i, t in texts.items():
        if _kotlin_blank(t):
            continue
        it = "i:" + split_side.stem_key(t)
        if src_item_override and i in src_item_override:
            it = src_item_override[i]
        c.execute("INSERT INTO source_row VALUES (?,?,?,?)", ("r:%d" % i, "mmlu_pro", i, it))
    ro.seal(c, cdb, "selftest")
    rows = []
    for i, t in texts.items():
        if _kotlin_blank(t) or i == drop_side_item:
            continue
        k = split_side.stem_key(t)
        corpora = "mc6-2026-09-11,mmlu-pro-v2" if i % 3 else "mmlu-pro-v2"
        if retag and i in retag:
            corpora = retag[i]
        rows.append(("i:" + k, "c:" + k, side_by_row[i], "MMLU_PRO", "cat", corpora))
    if foreign_eval:  # an EVAL item of the other corpus only: in the global reserved set, NOT in the pool id
        k = split_side.stem_key("Foreign union question")
        rows.append(("i:" + k, "c:" + k, "EVAL", "MATH", "Algebra", "mc6-2026-09-11"))
        k2 = split_side.stem_key("Foreign gate question")
        rows.append(("i:" + k2, "c:" + k2, "GATE", "MATH", "Algebra", "mc6-2026-09-11"))
    rows.sort(key=lambda r: r[0])
    table_sha = S._side_rows_sha(rows)
    side = os.path.join(tmp, "side.tsv")
    with open(side, "w", encoding="utf-8", newline="\n") as f:
        f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (S.SIDE_EXPORT_FORMAT, table_sha, len(rows), "0" * 64))
        f.write("\t".join(S.SIDE_COLS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    comps = sorted({r[1] for r in rows if r[2] == "EVAL" and "mmlu-pro-v2" in r[5].split(",")})
    return side, src, cdb, S.pool_id(comps, dev=False)


def selftest():
    import io
    import contextlib
    import shutil
    failures = []
    ran = []

    def case(name, fn):
        ran.append(name)
        try:
            fn()
            print("  ok   %s" % name)
        except (AssertionError, SystemExit, Exception) as e:  # a crash or an unexpected refusal is a FAIL too
            failures.append(name)
            print("  FAIL %s: %s: %s" % (name, type(e).__name__, e))

    def run(argv):
        buf = io.StringIO()
        code, err = None, None
        with contextlib.redirect_stdout(buf):
            try:
                code = main(argv, out=print)
            except SystemExit as e:
                err = str(e)
        return code, err, buf.getvalue()

    def argv_for(fx, dest, extra=()):
        side, src, cdb, pool = fx
        return ["--side", side, "--source-db", src, "--corpus-db", cdb, "--pool", pool, "--out", dest] + list(extra)

    def with_tmp(fn):
        def wrapped():
            tmp = tempfile.mkdtemp(prefix="v2pool_")
            try:
                fn(tmp)
            finally:
                for d, _ds, fs in os.walk(tmp):
                    for f in fs:
                        os.chmod(os.path.join(d, f), 0o666)
                shutil.rmtree(tmp, ignore_errors=True)
        return wrapped

    @with_tmp
    def accept(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "pool.json")
        code, err, text = run(argv_for(fx, dest))
        assert err is None and code == 0, (err, text)
        first = text.splitlines()[0]
        assert first.startswith("[ENGINE-POOL] pool %s recomputed" % fx[3]) and first.endswith("expected %s" % fx[3]), first
        assert "(4 EVAL components with a member in mmlu-pro-v2)" in first, first
        doc = json.load(open(dest, encoding="utf-8"))
        assert doc["eval_ids"] == [-1000009, 501, 502, 507], doc["eval_ids"]
        assert doc["gate_ids"] == [503, 508], doc["gate_ids"]
        assert doc["train_ids"] == [504, 505, 506, 510, 512], doc["train_ids"]
        assert doc["sentinel_ids"] == [-1000009], doc["sentinel_ids"]
        c = doc["counts"]
        assert (c["rows"], c["eval"], c["gate"], c["reserved"], c["train"], c["sentinels_reserved"]) == (11, 4, 2, 6, 5, 1), c
        assert c["global_reserved_items"] == 8, c  # 4 EVAL + 2 GATE of the corpus, + 1 EVAL + 1 GATE foreign
        assert doc["pool_id"] == fx[3] and doc["format"] == FORMAT and doc["rule"] == RULE
        assert ("ids: eval 4, gate 2, reserved 6 (sentinels reserved 1), train 5 (sentinels train 0); rows 11;"
                " global reserved items (all corpora) 8") in text, text
        raw = open(dest, "rb").read()
        assert b"\r" not in raw and raw.endswith(b"}\n")

    @with_tmp
    def dry_run(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "pool.json")
        code, err, text = run(argv_for(fx, dest, ["--dry-run"]))
        assert err is None and code == 0, err
        assert not os.path.exists(dest), "dry-run wrote the file"
        assert text.rstrip().endswith("DRY RUN: every check passed; nothing written (would write %s)" % dest), text

    @with_tmp
    def crlf_rendering(tmp):
        # a CRLF rendering of the same export (a Windows checkout) verifies to the same table_sha and sha256_lf
        fx = _fixture(tmp)
        items_lf, meta_lf = read_side(fx[0])
        crlf = os.path.join(tmp, "side_crlf.tsv")
        with open(crlf, "wb") as f:
            f.write(open(fx[0], "rb").read().replace(b"\n", b"\r\n"))
        items_cr, meta_cr = read_side(crlf)
        assert items_cr == items_lf and (meta_cr["table_sha"], meta_cr["sha256_lf"]) == (meta_lf["table_sha"], meta_lf["sha256_lf"])

    @with_tmp
    def s2_wrong_pool(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "pool.json")
        side, src, cdb, pool = fx
        code, err, _ = run(argv_for((side, src, cdb, "pv2_0000000000000000"), dest))
        assert err == "[ENGINE-POOL] REFUSED: S2: the side export's mmlu-pro-v2 pool is %s, not pv2_0000000000000000" % pool, err
        assert not os.path.exists(dest)

    @with_tmp
    def s1_tampered_export(tmp):
        fx = _fixture(tmp)
        side = fx[0]
        data = open(side, encoding="utf-8").read().replace("\tTRAIN\t", "\tEVAL\t", 1)
        with open(side, "w", encoding="utf-8", newline="\n") as f:
            f.write(data)
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[ENGINE-POOL] REFUSED: S1: side export") and "!= header" in err, err

    @with_tmp
    def s3_item_mismatch(tmp):
        fx = _fixture(tmp, src_item_override={5: "i:" + "0" * 64})
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[ENGINE-POOL] REFUSED: S3: 1 engine row(s) key to another item"), err

    @with_tmp
    def s3_row_mismatch(tmp):
        # the engine sees a row the ingest never saw: row 9's source_row removed by re-keying it to another pk
        fx = _fixture(tmp, extra_link=None, src_item_override=None)
        side, src, cdb, pool = fx
        os.chmod(cdb, 0o666)
        os.remove(cdb)
        c = ro.create_new(cdb)
        c.execute("CREATE TABLE source_row (source_row_id TEXT PRIMARY KEY, corpus_table TEXT NOT NULL,"
                  " upstream_pk INTEGER NOT NULL, item_id TEXT NOT NULL)")
        c.execute("INSERT INTO source_row VALUES ('r:1','mmlu_pro',1,'i:x')")
        ro.seal(c, cdb, "selftest")
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[ENGINE-POOL] REFUSED: S3: engine rows 11 vs corpus_v2 source_rows 1"), err

    @with_tmp
    def s4_missing_item(tmp):
        fx = _fixture(tmp, drop_side_item=6)
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[ENGINE-POOL] REFUSED: S4: engine row 6 (id 506) has item"), err

    @with_tmp
    def s4_foreign_corpus(tmp):
        fx = _fixture(tmp, retag={4: "mc6-2026-09-11"})
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err is not None and err.startswith("[ENGINE-POOL] REFUSED: S4: engine row 4 (id 504) item"), err
        assert err.endswith("is not tagged mmlu-pro-v2 (corpora ['mc6-2026-09-11'])"), err

    @with_tmp
    def s5_two_sides(tmp):
        # row 4 (TRAIN) and row 1 (EVAL) share the engine id 501 through a second link row
        fx = _fixture(tmp, extra_link={4: 501})
        code, err, _ = run(argv_for(fx, os.path.join(tmp, "p.json")))
        assert err == "[ENGINE-POOL] REFUSED: S5: engine id 501 carries two sides (EVAL, TRAIN)", err

    @with_tmp
    def s6_write_once(tmp):
        fx = _fixture(tmp)
        dest = os.path.join(tmp, "pool.json")
        assert run(argv_for(fx, dest))[0] == 0
        before = open(dest, "rb").read()
        code, err, _ = run(argv_for(fx, dest))
        assert err == "[ENGINE-POOL] REFUSED: S6: %s exists; the engine pool file is write-once" % dest, err
        assert open(dest, "rb").read() == before

    def committed_export():
        # the draw of record's committed export (a text file, no DB): S1 passes and S2 reproduces the pool of record
        items, meta = read_side(os.path.join(ROOT, DEFAULT_SIDE))
        assert meta["rows"] == 20544, meta
        assert pool_of(items, DEFAULT_CORPUS) == (DEFAULT_POOL, 3400), pool_of(items, DEFAULT_CORPUS)
        assert sum(1 for (_c, s, cs) in items.values() if s == "EVAL" and DEFAULT_CORPUS in cs) == 3492

    for name, fn in [("committed export reproduces pv2_41dbd3dbcd399df0 (3,400 components, 3,492 items)", committed_export),
                     ("accept path: ids, counts, first line", accept), ("dry-run writes nothing", dry_run),
                     ("CRLF rendering verifies to the LF pins", crlf_rendering),
                     ("S2 wrong pool id refused", s2_wrong_pool), ("S1 tampered export refused", s1_tampered_export),
                     ("S3 item mismatch refused", s3_item_mismatch), ("S3 row-set mismatch refused", s3_row_mismatch),
                     ("S4 item absent refused", s4_missing_item), ("S4 foreign-corpus item refused", s4_foreign_corpus),
                     ("S5 one id two sides refused", s5_two_sides), ("S6 write-once refused", s6_write_once)]:
        case(name, fn)
    print("[ENGINE-POOL] selftest: %d / %d passed" % (len(ran) - len(failures), len(ran)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
