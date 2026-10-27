"""EMBEDDER-PLUMBING (RP08), the Python read guard of the FLAT readers (docs/judge_v2_program.md L21754-L21772, section
"## Registered 2026-09-27 (before any code or call) - EMBEDDER-PLUMBING", registered at a357ef0 before any code). ZERO calls:
no judge, no LLM, no embedding call. Every DB is opened read-only through pool_guard.open_ro (a non-empty -wal / -journal
beside it REFUSES; mode=ro&immutable=1).

Question (verbatim in the programme): can the site null and the FLAT readers be made to read the embedding cache of the tree's
OWN embedder, fail-closed, with a guard that refuses a wrong-embedder read (cos(mean site vector, snapshot vmfMu) >= 0.99) and a
canonical-name cache guard, byte-inert on the qwen3 path and with both guard branches proved by execution?

This module is the Python twin of src/test/kotlin/taxonomy/EmbedderReadGuard.kt (the site-null harness's guard); the two agree
on the budget, the canonical tags, the native-dimension table and the printed lines ("[EMB-GUARD] ..."), and --selftest parses
the Kotlin sources to assert the tables are equal. Its callers (tools/analysis/flat_mix_mmlu.py: embedding_guard_flat, and
FLAT-GENERALITY's driver through it) run it BEFORE any partition fit:
  (c) VMFMU COSINE GUARD: for EVERY accepted split site of the snapshot (childIds >= 2 and dasguptaDeltaNorm > 0, the Kotlin
      harness's site list; it contains the root family whenever the root split), cos(normalised unweighted mean of the site's
      member vectors read from the OPENED cache, sliced to the slice width and unit-normalised, the snapshot's vmfMu) >= 0.99,
      else REFUSE. The minimum and the budget are printed on every run, pass or fail (CONTEXT rule 11); every site's cosine
      is printed on a refusal.
      DIMENSION CHECK: every raw vector read has exactly the named model's native dimension (NATIVE_DIM); an unknown model, a
      mixed-length read or a vmfMu whose length is not the slice width REFUSES. All findings are printed before refusing.
  (d) THE MODEL MUST BE NAMED: by the run manifest's embedding_model or an explicit --embedding-model (both, and different ->
      REFUSE); a manifest present without embedding_model and no explicit name REFUSES; no manifest and an explicit cache file
      without an explicit model REFUSES. (No manifest, no cache file and no model: the DB of record's canonical model; the FLAT
      readers always have a manifest, so this branch is the site null's -- ambiguity A1, flagged to the registrar.)
  (a)/(e) validate_cache_file: an explicit cache file must exist, carry the SQLite header, and hold the embeddings and queries
      tables, else REFUSE.
  (b) cache_file_for: EmbeddingCache.cacheFileFor's rule (only "", "qwen3-embedding", "qwen3-embedding:latest" route to
      embeddings_cache.db; every other tag, qwen3 variants included, to embeddings_cache_<sanitised>.db).

Launch sequence (engine-coder / reviewer; zero calls; synthetic only; opens no DB of record):
  python tools/analysis/embedder_guard.py --selftest    # every branch executed on synthetic caches in a temp dir
  python tools/analysis/embedder_guard.py --mutants     # every check removed in turn; every mutant must be KILLED
  python tools/analysis/embedder_guard.py --dry-run     # a synthetic end-to-end guard read (admit, then refuse); no DB of record
The proof legs of record (P-2 (vi): the FLAT reader refuses the nomic DB for af_clean_s42 and admits the qwen3 DB) are run by
the run-operator in a W-window after THREAD-CAP and the steward's WAL checkpoint (W0 RP02), through flat_mix_mmlu.py
--dry-run [--embedding-cache-file <nomic DB> --embedding-model nomic-embed-text:latest]; never by this module.
[CORRECTED 2026-09-27 by the engine-coder, READY_w0_rp08 M1 (bb30526): the bracket above is WRONG for the refusal leg. The model
named is the TREE's embedder; af_clean_s42's manifest names qwen3-embedding:latest, so an explicit nomic name refuses on the
CONTRADICTION branch before any cosine is read. The P-2 (vi) legs are: flat_mix_mmlu.py --dry-run --embedding-cache-file
<nomic DB> with NO --embedding-model (REFUSE, the cosine and the dimension printed), then flat_mix_mmlu.py --dry-run with no
flags (ADMIT).]
[2026-09-27, the engine-coder, READY_w0_rp08 F1 (H1): EG-MULTI executes the MULTI-SITE gate on a two-split-site tree (n1 the
root, n3 splitting B into n6 / n7): the correct tree is ADMITTED with each site's own region (n 120 / 60); a wrong vmfMu at the
SECOND site REFUSES with that site named as the minimum while the root alone reads >= 0.99 (a max-guard or a first-site-only
guard would admit); a NaN cosine at one site REFUSES on the undefined branch alone; a tree with no split site REFUSES with
"no site to check". Ruling R2 (programme L21831-L21846) is what is built: with no flag the DB of record and the canonical
model; any other embedder needs the explicit flag plus this guard.]
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy is imported (the author's cap: single-threaded)
    os.environ[_v] = "1"

import re
import sys
import json
import struct
import sqlite3
import argparse
import tempfile
import hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402

TAG = "[EMB-GUARD]"
COS_BUDGET = 0.99
CANONICAL_MODEL = "qwen3-embedding:latest"
DB_OF_RECORD = "embeddings_cache.db"
CANONICAL_TAGS = ("qwen3-embedding", "qwen3-embedding:latest")
NATIVE_DIM = {"qwen3-embedding:latest": 4096, "nomic-embed-text:latest": 768, "embeddinggemma:latest": 768,
              "mxbai-embed-large:latest": 1024}
SQLITE_MAGIC = b"SQLite format 3\x00"
KT_GUARD = os.path.join(ROOT, "src", "test", "kotlin", "taxonomy", "EmbedderReadGuard.kt")
KT_CACHE = os.path.join(ROOT, "src", "main", "kotlin", "taxonomy", "dataset", "EmbeddingCache.kt")


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def pins_of(path):
    data = open(path, "rb").read().replace(b"\r\n", b"\n")
    return "blob:%s / sha256-lf16:%s / sha256-crlf16:%s" % (hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()[:8],
                                                            hashlib.sha256(data).hexdigest()[:16],
                                                            hashlib.sha256(data.replace(b"\n", b"\r\n")).hexdigest()[:16])


# ------------------------------------------------------------------------------------------------ names
def canonical_model(tag):
    """Ollama naming: an untagged name means ':latest' (comparison and the dimension lookup only)."""
    t = tag.strip()
    return t if ":" in t else t + ":latest"


def cache_file_for(model):
    """EmbeddingCache.cacheFileFor (EMBEDDER-PLUMBING (b)): exact, case-sensitive, untrimmed."""
    if model.strip() == "" or model in CANONICAL_TAGS:
        return DB_OF_RECORD
    return "embeddings_cache_" + re.sub(r"[^A-Za-z0-9._-]", "_", model) + ".db"


def resolve_model(manifest, explicit, cache_file_set):
    """(d) -> (model, source). manifest: the run manifest as a dict, or None when none is reachable."""
    if explicit is not None and explicit.strip() == "":
        refuse("--embedding-model is present but blank")
    fm = manifest.get("embedding_model") if manifest is not None else None
    fm = fm if isinstance(fm, str) and fm.strip() else None
    if explicit is not None and fm is not None and canonical_model(explicit) != canonical_model(fm):
        refuse("--embedding-model=%r contradicts the run manifest's embedding_model=%r" % (explicit, fm))
    if explicit is not None:
        return explicit.strip(), "--embedding-model"
    if fm is not None:
        return fm, "run manifest embedding_model"
    if manifest is not None:
        refuse("the run manifest has no embedding_model and no --embedding-model names the model")
    if cache_file_set:
        refuse("--embedding-cache-file is set but neither a run manifest's embedding_model nor --embedding-model names the model "
               "its vectors must come from")
    return CANONICAL_MODEL, "default (no cache file, no model, no manifest: the DB of record's canonical model)"


def validate_cache_file(path):
    """(a) an explicit cache file: exists, a file, the SQLite header, the embeddings and queries tables."""
    if not os.path.exists(path):
        refuse("--embedding-cache-file %r does not exist" % path)
    if not os.path.isfile(path):
        refuse("--embedding-cache-file %r is not a regular file" % path)
    with open(path, "rb") as f:
        head = f.read(len(SQLITE_MAGIC))
    if head != SQLITE_MAGIC:
        refuse("--embedding-cache-file %r is not a SQLite database (header mismatch)" % path)
    con = pool_guard.open_ro(path)
    try:
        tables = set(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'"))
    finally:
        con.close()
    missing = [t for t in ("embeddings", "queries") if t not in tables]
    if missing:
        refuse("--embedding-cache-file %r lacks the table(s) %s the readers join (has %s)" % (path, missing, sorted(tables)))
    return path


# ------------------------------------------------------------------------------------------------ the read and the guard
def split_sites(byid):
    """The accepted split sites (childIds >= 2 and dasguptaDeltaNorm > 0), the Kotlin harness's list, in id order."""
    return [byid[k] for k in sorted(byid) if len(byid[k].get("childIds") or []) >= 2 and (byid[k].get("dasguptaDeltaNorm") or 0.0) > 0.0]


def read_vectors(con, ids, dim):
    """-> ({query id: unit vector sliced to dim}, {raw length in floats: count}). Big-endian float32 blobs."""
    out, dims = {}, {}
    ids = list(ids)
    for s in range(0, len(ids), 400):
        ch = ids[s:s + 400]
        sql = ("SELECT q.id, e.vector FROM queries q JOIN embeddings e ON e.query = q.distilled_text WHERE q.id IN (%s)"
               % ",".join("?" * len(ch)))
        for qid, blob in con.execute(sql, ch):
            if not isinstance(blob, bytes):
                continue
            n = len(blob) // 4
            dims[n] = dims.get(n, 0) + 1
            if n < dim:
                continue
            v = np.array(struct.unpack(">%df" % dim, blob[:4 * dim]), dtype=np.float64)
            nv = float(np.linalg.norm(v))
            if nv > 0:
                out[qid] = v / nv
    return out, dict(sorted(dims.items()))


def cosine(vectors, mu):
    """cos(normalised mean of the unit vectors, mu normalised); NaN when degenerate."""
    if not vectors:
        return float("nan")
    m = np.sum(np.stack(vectors), axis=0)
    mu = np.asarray(mu, dtype=np.float64)
    nm, nu = float(np.linalg.norm(m)), float(np.linalg.norm(mu))
    if nm <= 0 or nu <= 0:
        return float("nan")
    return float(m @ mu / (nm * nu))


def _fmt(x):
    return "NaN" if x != x else "%.4f" % x


def guard(con, cache_path, sites, region_ids, slice_dim, model, source):
    """(c) + the dimension check. Reads the union of the sites' member ids ONCE, prints, REFUSES on any finding."""
    ids_by = [(s, list(region_ids(s))) for s in sites]
    union = list(dict.fromkeys(q for _, ids in ids_by for q in ids))
    vec, dims = read_vectors(con, union, slice_dim)
    native = NATIVE_DIM.get(canonical_model(model))
    reasons = []
    if not sites:
        reasons.append("no site to check")
    if native is None:
        reasons.append("model %r has no declared native dimension (NATIVE_DIM: %s)" % (model, sorted(NATIVE_DIM)))
    elif set(dims) != {native}:
        reasons.append("raw vector dimensions %s != {%d} (the native dimension of %s)" % (dims, native, canonical_model(model)))
    rows = []
    for s, ids in ids_by:
        vs = [vec[q] for q in ids if q in vec]
        mu = s.get("vmfMu")
        if mu is None:
            reasons.append("site %s has no vmfMu" % s["id"])
            c = float("nan")
        elif len(mu) != slice_dim:
            reasons.append("site %s vmfMu length %d != slice width %d" % (s["id"], len(mu), slice_dim))
            c = float("nan")
        else:
            c = cosine(vs, mu)
        if not vs:
            reasons.append("site %s: no member vector recovered from the opened cache (%d ids)" % (s["id"], len(ids)))
        rows.append(dict(id=s["id"], label=(s.get("label") or s["id"]), n=len(ids), found=len(vs), cos=c))
    finite = [r for r in rows if r["cos"] == r["cos"]]
    worst = min(finite, key=lambda r: r["cos"]) if finite else None
    min_cos = worst["cos"] if (worst is not None and len(finite) == len(rows)) else float("nan")
    if min_cos == min_cos and min_cos < COS_BUDGET:
        reasons.append("min cosine %.4f < budget %.2f" % (min_cos, COS_BUDGET))
    if min_cos != min_cos and rows:
        reasons.append("the cosine is undefined on %d site(s)" % (len(rows) - len(finite)))
    admitted = not reasons
    cs = sorted(r["cos"] for r in finite)
    median = cs[len(cs) // 2] if cs else float("nan")
    print("%s model=%s (%s); cache=%s; native dim expected %s; vectors read %d of %d ids, raw dims %s; slice width %d"
          % (TAG, model, source, cache_path, native if native is not None else "UNKNOWN", len(vec), len(union), dims, slice_dim))
    print("%s vmfMu cosine over %d sites: min %s (site %s), median %s; budget %.2f -> %s"
          % (TAG, len(rows), _fmt(min_cos), ("%s '%s' n=%d" % (worst["id"], worst["label"][:40], worst["n"])) if worst else "-",
             _fmt(median), COS_BUDGET, "ADMIT" if admitted else "REFUSE"))
    for r in (sorted(finite, key=lambda r: r["cos"])[:3] if admitted else rows):
        print("%s   site %-10s n=%-5d found=%-5d cos=%s  %s" % (TAG, r["id"], r["n"], r["found"], _fmt(r["cos"]), r["label"][:50]))
    res = dict(admitted=admitted, min_cos=min_cos, rows=rows, dims=dims, reasons=reasons)
    if not admitted:
        refuse("before any partition fit: " + "; ".join(reasons))
    return res


def guard_file(cache_path, byid, region_ids, slice_dim, model, source):
    """Open the cache read-only (pool_guard.open_ro), run guard() on the snapshot's split sites, close."""
    con = pool_guard.open_ro(cache_path)
    try:
        return guard(con, cache_path, split_sites(byid), region_ids, slice_dim, model, source)
    finally:
        con.close()


# ------------------------------------------------------------------------------------------------ selftest
class _Checks(object):
    def __init__(self, quiet=False):
        self.n = 0
        self.quiet = quiet

    def ok(self, cond, what):
        self.n += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not self.quiet:
            print("  ok  " + what)


def _refusal(fn, needle):
    try:
        fn()
    except SystemExit as e:
        return needle in str(e)
    return False


def _blob(v):
    return struct.pack(">%df" % len(v), *[float(x) for x in v])


def _make_cache(path, rows, queries=True, embeddings=True):
    """A synthetic cache in a temp dir (selftest only). The writer is the RAW sqlite3.connect: a caller's read-only connect guard
    (flat_mix_mmlu's) keeps the original under ._raw."""
    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(path)
    if embeddings:
        c.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    if queries:
        c.execute("CREATE TABLE queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, "
                  "ground_truth_category TEXT DEFAULT '', query_id INTEGER DEFAULT -1)")
    if queries and embeddings:
        for qid, v in rows.items():
            c.execute("INSERT INTO queries (id, raw_text, distilled_text) VALUES (?, ?, ?)", (qid, "text " + qid, "text " + qid))
            c.execute("INSERT INTO embeddings (query, vector) VALUES (?, ?)", ("text " + qid, _blob(v)))
    c.commit()
    c.close()
    return path


def synthetic(rng, slice_dim=256):
    """Two clusters of 4096-d vectors, a three-node tree whose vmfMu are the fitter's (normalised mean of sliced unit vectors)."""
    ida, idb = ["q_a%02d" % i for i in range(60)], ["q_b%02d" % i for i in range(60)]
    da, db = rng.standard_normal(4096) * 0.05, rng.standard_normal(4096) * 0.05
    vec = {q: da + 0.02 * rng.standard_normal(4096) for q in ida}
    vec.update({q: db + 0.02 * rng.standard_normal(4096) for q in idb})

    def mu(ids):
        m = np.sum([vec[q][:slice_dim] / np.linalg.norm(vec[q][:slice_dim]) for q in ids], axis=0)
        return list(m / np.linalg.norm(m))
    byid = {"n1": dict(id="n1", label="ROOT", depth=0, childIds=["n2", "n3"], queryIds=[], vmfMu=mu(ida + idb), dasguptaDeltaNorm=0.2),
            "n2": dict(id="n2", label="A", depth=1, childIds=[], queryIds=ida, vmfMu=mu(ida), dasguptaDeltaNorm=0.0),
            "n3": dict(id="n3", label="B", depth=1, childIds=[], queryIds=idb, vmfMu=mu(idb), dasguptaDeltaNorm=0.0)}
    return vec, byid, ida + idb


def synthetic_two_site(rng, slice_dim=256):
    """synthetic() with a SECOND accepted split site: n3 (B) splits into n6 = B[:30] and n7 = B[30:] (READY_w0_rp08 F1).
    Sites in id order: n1 (root, 120 ids), n3 (60 ids)."""
    vec, byid, ids = synthetic(rng, slice_dim)
    idb = list(byid["n3"]["queryIds"])

    def mu(q_ids):
        m = np.sum([vec[q][:slice_dim] / np.linalg.norm(vec[q][:slice_dim]) for q in q_ids], axis=0)
        return list(m / np.linalg.norm(m))
    byid["n3"] = dict(byid["n3"], childIds=["n6", "n7"], queryIds=[], dasguptaDeltaNorm=0.1)
    byid["n6"] = dict(id="n6", label="B1", depth=2, childIds=[], queryIds=idb[:30], vmfMu=mu(idb[:30]), dasguptaDeltaNorm=0.0)
    byid["n7"] = dict(id="n7", label="B2", depth=2, childIds=[], queryIds=idb[30:], vmfMu=mu(idb[30:]), dasguptaDeltaNorm=0.0)
    return vec, byid, ids


def _guard_out(fn):
    """-> (printed text, refusal message or None, return value or None)."""
    import io
    import contextlib
    buf = io.StringIO()
    msg, res = None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as e:
            msg = str(e)
    return buf.getvalue(), msg, res


def region(byid, nid):
    out, st, seen = {}, [nid], set()
    while st:
        c = st.pop()
        if c in seen:
            continue
        seen.add(c)
        for q in byid[c].get("queryIds") or []:
            out.setdefault(q, None)
        st.extend(x for x in byid[c].get("childIds") or [] if x in byid)
    return list(out)


def selftest(only=None, quiet=False):
    chk = _Checks(quiet)
    sel = (lambda name: only is None or name in only)
    rng = np.random.default_rng(20260927)
    vec, byid, ids = synthetic(rng)
    reg = lambda s: region(byid, s["id"])
    if sel("EG-THREADS"):
        chk.ok(all(os.environ.get(v) == "1" for v in THREAD_VARS), "EG-THREADS the three thread variables are 1")
    with tempfile.TemporaryDirectory() as td:
        right = _make_cache(os.path.join(td, "embeddings_cache.db"), vec)
        if sel("EG-ADMIT"):
            r = guard_file(right, byid, reg, 256, "qwen3-embedding:latest", "selftest")
            chk.ok(r["admitted"] and r["min_cos"] >= COS_BUDGET and r["dims"] == {4096: 120},
                   "EG-ADMIT the right embedder is ADMITTED (min cos %.4f >= 0.99, raw dims {4096: 120})" % r["min_cos"])
            chk.ok(len(split_sites(byid)) == 1 and split_sites(byid)[0]["id"] == "n1", "EG-ADMIT the checked sites are the accepted split sites")
        if sel("EG-WRONG"):
            nomic = _make_cache(os.path.join(td, "embeddings_cache_nomic-embed-text_latest.db"),
                                {q: rng.standard_normal(768) for q in ids})
            chk.ok(_refusal(lambda: guard_file(nomic, byid, reg, 256, "qwen3-embedding:latest", "selftest"), "!= {4096}"),
                   "EG-WRONG a 768-d wrong-embedder cache is REFUSED (dimension)")
            chk.ok(_refusal(lambda: guard_file(nomic, byid, reg, 256, "qwen3-embedding:latest", "selftest"), "< budget 0.99"),
                   "EG-WRONG ... and by the cosine")
            con = pool_guard.open_ro(nomic)
            try:
                v2, _ = read_vectors(con, ids, 256)
            finally:
                con.close()
            c = cosine([v2[q] for q in ids], byid["n1"]["vmfMu"])
            chk.ok(abs(c) < 0.2, "EG-WRONG the wrong-embedder cosine is %.4f (|cos| < 0.2)" % c)
        if sel("EG-COS"):
            w4096 = _make_cache(os.path.join(td, "w4096.db"), {q: rng.standard_normal(4096) for q in ids})
            try:
                guard_file(w4096, byid, reg, 256, "qwen3-embedding:latest", "selftest")
                msg = ""
            except SystemExit as e:
                msg = str(e)
            chk.ok("< budget 0.99" in msg and "raw vector dimensions" not in msg, "EG-COS the cosine branch alone refuses (right dim, wrong vectors)")
        if sel("EG-DIM"):
            try:
                guard_file(right, byid, reg, 256, "nomic-embed-text", "selftest")
                msg = ""
            except SystemExit as e:
                msg = str(e)
            chk.ok("{4096: 120} != {768}" in msg and "budget" not in msg, "EG-DIM the dimension branch alone refuses (right vectors, 768-d model)")
            mixed = dict(vec)
            mixed[ids[0]] = rng.standard_normal(768)
            mx = _make_cache(os.path.join(td, "mixed.db"), mixed)
            chk.ok(_refusal(lambda: guard_file(mx, byid, reg, 256, "qwen3-embedding:latest", "selftest"), "{768: 1, 4096: 119}"),
                   "EG-DIM a mixed-length read REFUSES (768 > 256 passed the old check)")
            chk.ok(_refusal(lambda: guard_file(right, byid, reg, 256, "some-new-embedder:v1", "selftest"), "no declared native dimension"),
                   "EG-DIM an unknown model REFUSES")
            bad = json.loads(json.dumps(byid))
            bad["n1"]["vmfMu"] = bad["n1"]["vmfMu"] + [0.0] * 256
            chk.ok(_refusal(lambda: guard_file(right, bad, lambda s: region(bad, s["id"]), 256, "qwen3-embedding:latest", "selftest"),
                            "vmfMu length 512 != slice width 256"), "EG-DIM a vmfMu of the wrong length REFUSES")
        if sel("EG-MULTI"):
            st_multi(chk, td, rng)
        if sel("EG-FILE"):
            chk.ok(_refusal(lambda: validate_cache_file(os.path.join(td, "absent.db")), "does not exist"), "EG-FILE a missing file REFUSES")
            chk.ok(_refusal(lambda: validate_cache_file(td), "not a regular file"), "EG-FILE a directory REFUSES")
            txt = os.path.join(td, "not_sqlite.db")
            with open(txt, "w") as f:
                f.write("hello, not a database")
            chk.ok(_refusal(lambda: validate_cache_file(txt), "not a SQLite database"), "EG-FILE a non-SQLite file REFUSES")
            ne = _make_cache(os.path.join(td, "noemb.db"), {}, queries=True, embeddings=False)
            chk.ok(_refusal(lambda: validate_cache_file(ne), "['embeddings']"), "EG-FILE a cache without the embeddings table REFUSES")
            nq = _make_cache(os.path.join(td, "noq.db"), {}, queries=False, embeddings=True)
            chk.ok(_refusal(lambda: validate_cache_file(nq), "['queries']"), "EG-FILE a cache without the queries table REFUSES")
            chk.ok(validate_cache_file(right) == right, "EG-FILE a valid cache passes")
    if sel("EG-MODEL"):
        chk.ok(_refusal(lambda: resolve_model({"seed": 42}, None, False), "no embedding_model"), "EG-MODEL a manifest without embedding_model and no name REFUSES")
        chk.ok(_refusal(lambda: resolve_model({"embedding_model": " "}, None, False), "no embedding_model"), "EG-MODEL a blank manifest model counts as absent")
        chk.ok(_refusal(lambda: resolve_model(None, None, True), "neither"), "EG-MODEL a cache file without a model name REFUSES")
        chk.ok(_refusal(lambda: resolve_model(None, "", False), "blank"), "EG-MODEL a blank explicit model REFUSES")
        chk.ok(_refusal(lambda: resolve_model({"embedding_model": "qwen3-embedding:latest"}, "nomic-embed-text:latest", False), "contradicts"),
               "EG-MODEL an explicit model contradicting the manifest REFUSES")
        chk.ok(resolve_model({"embedding_model": "qwen3-embedding:latest"}, "qwen3-embedding", False)[0] == "qwen3-embedding",
               "EG-MODEL an untagged explicit name equal to the manifest's (Ollama :latest) is admitted")
        chk.ok(resolve_model({"embedding_model": "qwen3-embedding:latest"}, None, True) == ("qwen3-embedding:latest", "run manifest embedding_model"),
               "EG-MODEL the manifest names the model")
        chk.ok(resolve_model(None, None, False)[0] == CANONICAL_MODEL, "EG-MODEL nothing set: the DB of record's canonical model (A1)")
        chk.ok(_refusal(lambda: resolve_model({"embedding_model": "qwen3-embedding:latest"}, "qwen3-embedding:8b", False), "contradicts"),
               "EG-MODEL a variant tag of the manifest's model (qwen3-embedding:8b) is a CONTRADICTION, not the same model")
    if sel("EG-ROUTE"):
        cases = {"": DB_OF_RECORD, "qwen3-embedding": DB_OF_RECORD, "qwen3-embedding:latest": DB_OF_RECORD,
                 "qwen3-embedding:8b": "embeddings_cache_qwen3-embedding_8b.db", "qwen3-embedding-instruct": "embeddings_cache_qwen3-embedding-instruct.db",
                 "qwen3-embedding:Latest": "embeddings_cache_qwen3-embedding_Latest.db",
                 "nomic-embed-text:latest": "embeddings_cache_nomic-embed-text_latest.db", "nomic-embed-text": "embeddings_cache_nomic-embed-text.db"}
        chk.ok(all(cache_file_for(m) == f for m, f in cases.items()), "EG-ROUTE cache_file_for: canonical tags -> the DB of record; variants own files")
    if sel("EG-PARITY"):
        kt = open(KT_GUARD, encoding="utf-8").read()
        block = kt[kt.index("val NATIVE_DIM"):]
        block = block[:block.index(")\n") + 1] if ")\n" in block else block[:block.index(")\r\n") + 1]
        ktdim = {m: int(d) for m, d in re.findall(r'"([^"]+)" to (\d+)', block)}
        chk.ok(ktdim == NATIVE_DIM, "EG-PARITY NATIVE_DIM equals EmbedderReadGuard.kt's (%d models)" % len(ktdim))
        chk.ok(re.search(r"const val COS_BUDGET = ([0-9.]+)", kt).group(1) == repr(COS_BUDGET), "EG-PARITY COS_BUDGET equals the Kotlin guard's")
        kc = open(KT_CACHE, encoding="utf-8").read()
        tags = tuple(re.findall(r'"([^"]+)"', re.search(r"CANONICAL_TAGS: Set<String> = setOf\(([^)]*)\)", kc).group(1)))
        chk.ok(tags == CANONICAL_TAGS, "EG-PARITY CANONICAL_TAGS equals EmbeddingCache.kt's")
    return chk.n


def _unit_mean_cos(vec, ids, mu, dim=256):
    return cosine([np.asarray(vec[q][:dim]) / np.linalg.norm(vec[q][:dim]) for q in ids], mu)


def st_multi(chk, td, rng):
    """READY_w0_rp08 F1: the multi-site gate with KNOWN expected values (the minimum's site, its value, per-site regions)."""
    vec, byid, ids = synthetic_two_site(rng)
    cache = _make_cache(os.path.join(td, "two_site.db"), vec)
    chk.ok([s["id"] for s in split_sites(byid)] == ["n1", "n3"], "EG-MULTI the two accepted split sites are n1 and n3, in id order")
    out, msg, res = _guard_out(lambda: guard_file(cache, byid, lambda s: region(byid, s["id"]), 256, "qwen3-embedding:latest", "selftest"))
    chk.ok(msg is None and res is not None and bool(res["admitted"])
           and [(r["id"], r["n"], r["found"]) for r in res["rows"]] == [("n1", 120, 120), ("n3", 60, 60)],
           "EG-MULTI the correct two-site tree is ADMITTED, each site read on its OWN region (n1 120/120, n3 60/60)")
    exp = {s: _unit_mean_cos(vec, region(byid, s), byid[s]["vmfMu"]) for s in ("n1", "n3")}
    chk.ok(res is not None and abs(res["min_cos"] - min(exp.values())) < 1e-12 and "over 2 sites" in out,
           "EG-MULTI min_cos = the minimum over BOTH sites (%.6f), printed 'over 2 sites'" % min(exp.values()))
    bad = json.loads(json.dumps(byid))
    bad["n3"]["vmfMu"] = list(byid["n2"]["vmfMu"])            # n3's vmfMu is A's: a wrong vector at the SECOND site only
    c3 = _unit_mean_cos(vec, region(bad, "n3"), bad["n3"]["vmfMu"])
    chk.ok(exp["n1"] >= COS_BUDGET and c3 < 0.5, "EG-MULTI fixture: root cos %.4f >= 0.99, n3 wrong-vmfMu cos %.4f < 0.5" % (exp["n1"], c3))
    out, msg, _ = _guard_out(lambda: guard_file(cache, bad, lambda s: region(bad, s["id"]), 256, "qwen3-embedding:latest", "selftest"))
    chk.ok(msg is not None and ("min cosine %.4f < budget 0.99" % c3) in msg and ("min %.4f (site n3 'B'" % c3) in out
           and "raw vector dimensions" not in msg,
           "EG-MULTI a wrong vmfMu at the second site REFUSES, n3 named as the minimum (%.4f); the root alone would admit" % c3)
    nan = json.loads(json.dumps(byid))
    nan["n3"]["vmfMu"] = [0.0] * 256
    out, msg, _ = _guard_out(lambda: guard_file(cache, nan, lambda s: region(nan, s["id"]), 256, "qwen3-embedding:latest", "selftest"))
    chk.ok(msg is not None and msg.endswith("before any partition fit: the cosine is undefined on 1 site(s)"),
           "EG-MULTI a NaN cosine at one site REFUSES on the undefined branch alone")
    leaf = {"n1": dict(id="n1", label="ROOT", depth=0, childIds=[], queryIds=list(ids), vmfMu=byid["n1"]["vmfMu"], dasguptaDeltaNorm=0.0)}
    out, msg, _ = _guard_out(lambda: guard_file(cache, leaf, lambda s: region(leaf, s["id"]), 256, "qwen3-embedding:latest", "selftest"))
    chk.ok(msg is not None and "no site to check" in msg and "over 0 sites" in out, "EG-MULTI a tree with no split site REFUSES: 'no site to check'")


MUTANTS = (
    ("cosine budget check removed", "    if min_cos == min_cos and min_cos < COS_BUDGET:\n", "    if False:\n", ("EG-COS",)),
    ("cosine budget read as 0.9", "COS_BUDGET = 0.99\n", "COS_BUDGET = 0.9\n", ("EG-PARITY",)),
    ("dimension check removed", "    elif set(dims) != {native}:\n", "    elif False:\n", ("EG-DIM",)),
    ("dimension check as the old vacuous one", "    elif set(dims) != {native}:\n", "    elif min(dims or [0]) < slice_dim:\n", ("EG-DIM",)),
    ("unknown model admitted", "    if native is None:\n        reasons.append", "    if False:\n        reasons.append", ("EG-DIM",)),
    ("vmfMu length unchecked", "        elif len(mu) != slice_dim:\n", "        elif False:\n", ("EG-DIM",)),
    ("refusal not raised", "    if not admitted:\n        refuse(", "    if False:\n        refuse(", ("EG-WRONG",)),
    ("mean read from the snapshot, not the cache", "            c = cosine(vs, mu)\n", "            c = 1.0\n", ("EG-COS",)),
    ("manifest without model admitted", "    if manifest is not None:\n        refuse(", "    if False:\n        refuse(", ("EG-MODEL",)),
    ("cache file without model admitted", "    if cache_file_set:\n        refuse(", "    if False:\n        refuse(", ("EG-MODEL",)),
    ("contradiction admitted", "    if explicit is not None and fm is not None and canonical_model(explicit) != canonical_model(fm):\n",
     "    if False:\n", ("EG-MODEL",)),
    ("SQLite header unchecked", "    if head != SQLITE_MAGIC:\n", "    if False:\n", ("EG-FILE",)),
    ("tables unchecked", "    if missing:\n        refuse(\"--embedding-cache-file", "    if False:\n        refuse(\"--embedding-cache-file", ("EG-FILE",)),
    ("routing by prefix (the pre-RP08 rule)", "    if model.strip() == \"\" or model in CANONICAL_TAGS:\n",
     "    if model.strip() == \"\" or model.startswith(\"qwen3-embedding\"):\n", ("EG-ROUTE",)),
    ("sites include every node", "if len(byid[k].get(\"childIds\") or []) >= 2 and (byid[k].get(\"dasguptaDeltaNorm\") or 0.0) > 0.0]",
     "if True]", ("EG-ADMIT",)),
    ("threads not pinned", "for _v in THREAD_VARS:                       # BEFORE numpy", "for _v in ():                       # BEFORE numpy", ("EG-THREADS",)),
    ("X1 min cosine over sites -> max", "    worst = min(finite, key=lambda r: r[\"cos\"]) if finite else None",
     "    worst = max(finite, key=lambda r: r[\"cos\"]) if finite else None", ("EG-MULTI",)),
    ("X2 only the first split site checked", "(byid[k].get(\"dasguptaDeltaNorm\") or 0.0) > 0.0]\n",
     "(byid[k].get(\"dasguptaDeltaNorm\") or 0.0) > 0.0][:1]\n", ("EG-MULTI",)),
    ("X2b guard reads only the first site", "    ids_by = [(s, list(region_ids(s))) for s in sites]\n",
     "    ids_by = [(s, list(region_ids(s))) for s in sites[:1]]\n", ("EG-MULTI",)),
    ("X4 variant tag equals canonical (prefix compare)", "canonical_model(explicit) != canonical_model(fm):",
     "explicit.split(':')[0] != fm.split(':')[0]:", ("EG-MODEL",)),
    ("X6 no-site tree admitted", "    if not sites:\n        reasons.append", "    if False:\n        reasons.append", ("EG-MULTI",)),
    ("X7 NaN cosine sites admitted", "    if min_cos != min_cos and rows:\n", "    if False:\n", ("EG-MULTI",)),
)


def _exec_selftest(src, tests):
    saved = {v: os.environ.get(v) for v in THREAD_VARS}
    ns = {"__name__": "embedder_guard_mutant", "__file__": os.path.abspath(__file__)}
    try:
        for v in THREAD_VARS:
            os.environ.pop(v, None)
        exec(compile(src, "<mutant>", "exec"), ns)
        ns["selftest"](only=set(tests), quiet=True)
        return True
    except BaseException as e:                   # noqa: B902
        return "%s: %s" % (type(e).__name__, str(e)[:120])
    finally:
        for v, x in saved.items():
            os.environ[v] = x


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index(chr(10) + "MUTANTS = (")
    head, tail = src[:cut], src[cut:]
    print("MUTANTS (%d): each removes or alters one check; KILLED iff the targeted selftest subset fails" % len(MUTANTS))
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: the target text occurs %d times (must be exactly 1)" % (TAG, name, head.count(old)))
        ok_orig = _exec_selftest(src, tests)
        res = _exec_selftest(head.replace(old, new) + tail, tests)
        k = (res is not True) and ok_orig is True
        killed += int(k)
        print("  %-44s tests %-11s original %-4s mutant %-8s | %s" % (name, ",".join(tests), "PASS" if ok_orig is True else "FAIL",
                                                                    "KILLED" if k else "SURVIVED", "" if res is True else res[:100]))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def dry_run():
    """A synthetic end-to-end read: admit on the right cache, refuse on the wrong one. No DB of record is opened."""
    print("%s --dry-run: synthetic caches in a temp dir only; no DB of record is opened; no statistic of any registered test" % TAG)
    rng = np.random.default_rng(7)
    vec, byid, ids = synthetic(rng)
    with tempfile.TemporaryDirectory() as td:
        right = _make_cache(os.path.join(td, "embeddings_cache.db"), vec)
        wrong = _make_cache(os.path.join(td, "embeddings_cache_nomic-embed-text_latest.db"), {q: rng.standard_normal(768) for q in ids})
        model, source = resolve_model({"embedding_model": "qwen3-embedding:latest"}, None, False)
        guard_file(right, byid, lambda s: region(byid, s["id"]), 256, model, source)
        try:
            guard_file(wrong, byid, lambda s: region(byid, s["id"]), 256, model, source)
            print("%s DRY-RUN UNEXPECTED: the wrong cache was admitted" % TAG)
            return 1
        except SystemExit as e:
            print("(refusal raised as designed: %s)" % str(e)[:160])
    print("%s dry-run complete: nothing written, no DB of record opened" % TAG)
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--dry-run"):
        g.add_argument(f, action="store_true")
    a = ap.parse_args(argv)
    print("pool - (EMBEDDER-PLUMBING engineering module: synthetic only; no pool is read)")
    print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    print("[SCRIPT] tools/analysis/embedder_guard.py %s" % pins_of(os.path.abspath(__file__)))
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run()
    n = selftest()
    print("SELFTEST PASSED: %d checks" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
