"""EMBED-QUANT writer: embeds S0's text set with qwen3-embedding:8b-q8_0 (RAW) into intent_emb_qwen3_q8.db.

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — EMBED-QUANT: is qwen3-embedding's
Q4_K_M quantisation a confound of the intent-corpus embedder contrasts, ...", span L22738-L22760 _as_of 28b4032b (drafted in
docs/agents/plans/2026-10-02_next_registrations.md section 4, ce0d0f17). The registration's INSTRUMENT line names "a model-tag flag on
embedder_arms.py's writer"; this separate script is the builder's reading QB1 (printed by the readout; the registrar confirms or
brackets). This writer posts EMBEDDINGS only (Ollama /api/embed), never a judge call.

WHY A SEPARATE SCRIPT. tools/analysis/intent_transfer_s0.py (blob:f662ceb19738f515972871f5963f5dcfc764a271, asserted at every entry
point) is imported UNCHANGED: its blob is pinned in the intent_meta of the three S0 embedding DBs, so a model-tag flag on it would
orphan them. Its machinery does every read and the text set: pin_check / raw_pin_check (experiment_configs/intent_transfer_s0_pins.json,
strict: every pin set), load_corpora, text_set (the 57,350 texts, sha256-ordered), check_emb_dir / check_emb_target (no cache of
record, nothing under experiment_results/), check_meta / present_texts, record_table_hashes (the shared caches before and after),
_foreign_heavy (no JVM beside the embedding). embedder_arms (EA) does every POST and every write: ollama_embed (one keep-alive
connection, bounded whole-batch retry on transient connection errors, EMB-CONN), write_vectors (whole batches, INSERT OR IGNORE,
commit per batch: resumable), model_digest (/api/tags), and the EMB-PACE flags --pace-s / --tw-drain (off by default).

THE ARM. embedder "qwen3_q8", model tag qwen3-embedding:8b-q8_0, protocol RAW (no prefix, no transform), native dim 4096, file
intent_emb_qwen3_q8.db under --emb-dir (default DATA_ROOT = TAXOARENA_DATA_ROOT or the repo root). The tag is unknown to
embedder_guard.NATIVE_DIM and to S0's MODEL map; q8_registered() adds it to both dicts IN MEMORY for the duration of one call and
removes it in a finally (no file of either module changes; the selftest asserts the dicts are restored).

FILE PINS (intent_meta, first launch, exclusive create "xb"): S0's expected_meta fields (text-set sha256 and count, ingest DB sha256,
S0's script blob, embedder_arms' blob, protocol RAW, native dim) with embedder qwen3_q8 and model qwen3-embedding:8b-q8_0, plus
writer_blob_lf (this file's LF blob), quant Q8_0 and model_digest (the tag's /api/tags digest). A later launch RESUMES only under
identical pins (a re-pulled tag, another writer blob or another text set REFUSES; the file is then discarded, never re-pinned).

TRANSPORT PREFLIGHT (in --dry-run, and before any --go write):
  T1 the resolved Ollama URL is printed; the tag must be LISTED by /api/tags with a digest (a pull still in progress REFUSES), and its
     digest must differ from qwen3-embedding:latest's (the same weights under two tags REFUSES: there would be nothing to compare).
  T2 the first PARITY_N = 20 texts of the set (sha256 order) are posted to the Q8 tag: every vector 4096-d, finite, non-zero (else
     REFUSES). cos(Q8, Q4) per text against S0's stored qwen3 vectors (intent_emb_qwen3.db, pinned) after slice d + renormalise,
     d in {256, 1024, 4096}: min and median PRINTED, NO BAR (route parity against Q4 is not defined: they are different models).
  T3 repeatability: the same 20 texts posted again; cos(first, second) after slice 256 + renormalise, min >= 0.998 (S0's qwen3 parity
     bar, PARITY_BAR["qwen3"], the orchestrator's 2026-09-30 ruling) else REFUSES.
  T4 resume parity: when intent_emb_qwen3_q8.db already holds rows, the first 20 STORED rows (sha256 order) are re-embedded and
     compared with the stored vectors (slice 256 + renormalise, min >= 0.998) else REFUSES (S0's route-parity rule on the arm's own file).
  --dry-run adds a timed probe (PROBE_N texts posted, nothing written) and prices the full embedding. The free disk space of the
  --emb-dir volume is printed in the dry-run and before and after every --go (the registration's HYGIENE line; the pull itself is
  the operator's).

LAUNCH (run-operator; zero judge calls; one heavy process: no java.exe, nothing else on Ollama):
  python tools/analysis/embed_quant_writer.py --selftest
  python tools/analysis/embed_quant_writer.py --mutants
  python tools/analysis/embed_quant_writer.py --dry-run                 # pins, text set, T1-T4, probe price; writes nothing
  python tools/analysis/embed_quant_writer.py --embed --limit 500 --go  # optional pilot rows (resumable)
  python tools/analysis/embed_quant_writer.py --embed --go              # complete (resumes); then the registrar pins the file
  (the registrar pins intent_emb_qwen3_q8.db in experiment_configs/embed_quant_pins.json; tools/analysis/embed_quant.py reads it)

MUTANT TABLE: `--mutants` and the commit message: 21 of 21 KILLED at build (20 by an assertion, 'dimension check removed' by the
crash it causes downstream). Selftest 44 checks, stubs only (in-process embed_fn / digest_fn, and embedder_arms' stub Ollama on
127.0.0.1 for the real ollama_embed / model_digest path); nothing real is contacted.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy: the CPU lane is single-threaded
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import shutil          # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile; import scratch_dir        # noqa: E402
import time            # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import intent_transfer_s0 as ITS      # noqa: E402  (imported unchanged; blob asserted)
from data_v2 import ro as RO          # noqa: E402
EA = ITS.EA
II = ITS.II

TAG = "[EMBED-QUANT-W]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
E_Q8 = "qwen3_q8"
MODEL_Q8 = "qwen3-embedding:8b-q8_0"
MODEL_Q4 = ITS.MODEL["qwen3"]
NATIVE = 4096
QUANT = "Q8_0"
ARM_Q8 = EA.Arm("qwen3_q8_raw", MODEL_Q8, "PRIMARY", "", False)
PARITY_N = 20
SELF_BAR = ITS.PARITY_BAR["qwen3"]
COS_SLICES = (256, 1024, 4096)
PROBE_N = 500


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_its_blob():
    got = RO.git_blob_lf(ITS.__file__)
    if got != ITS_BLOB:
        refuse("intent_transfer_s0.py is blob %s, not %s: S0's machinery must be imported unchanged" % (got, ITS_BLOB))
    return got


def writer_blob():
    return RO.git_blob_lf(os.path.abspath(__file__))


@contextlib.contextmanager
def q8_registered():
    """The Q8 tag in embedder_guard.NATIVE_DIM and in S0's MODEL map, in memory only, for one call; removed in a finally."""
    add_dim = MODEL_Q8 not in EA.EG.NATIVE_DIM
    add_model = E_Q8 not in ITS.MODEL
    if add_dim:
        EA.EG.NATIVE_DIM[MODEL_Q8] = NATIVE
    if add_model:
        ITS.MODEL[E_Q8] = MODEL_Q8
    try:
        yield
    finally:
        if add_dim:
            EA.EG.NATIVE_DIM.pop(MODEL_Q8, None)
        if add_model:
            ITS.MODEL.pop(E_Q8, None)


def q8_path(emb_dir):
    return ITS.emb_path(E_Q8, emb_dir)


def expected_meta_q8(set_sha, n_texts, ingest_sha):
    m = ITS.expected_meta("qwen3", set_sha, n_texts, ingest_sha)
    m.update({"embedder": E_Q8, "model": MODEL_Q8, "native_dim": str(NATIVE), "quant": QUANT, "writer_blob_lf": writer_blob()})
    return m


def disk_line(emb_dir, when):
    free = shutil.disk_usage(emb_dir).free
    print("%s DISK %s: %.2f GB free on the volume of %s" % (TAG, when, free / 1e9, emb_dir))
    return free


def heavy_check():
    heavy = ITS._foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): one heavy process at a time; the embedding waits" % heavy[:3])


def load_inputs(db, emb_dir):
    """S0's pins (strict: every raw / ingest / qwen3 pin set and equal), S0's text set, the Q4 file's meta."""
    check_its_blob()
    sha = {"ingest_db": ITS.pin_check(db, "ingest_db", True)}
    ITS.raw_pin_check(db, True)
    q4 = ITS.emb_path("qwen3", emb_dir)
    sha["qwen3"] = ITS.pin_check(q4, "emb", True, sub="qwen3", label="intent_emb_qwen3.db")
    CS = ITS.load_corpora(db)
    texts, set_sha, _d = ITS.text_set(CS)
    ITS.check_meta(q4, ITS.expected_meta("qwen3", set_sha, len(texts), sha["ingest_db"]))
    return sha, texts, set_sha


def after_check(sha, db, emb_dir):
    for k, s in sha.items():
        now = II.file_sha(db if k == "ingest_db" else ITS.emb_path(k, emb_dir))
        if now != s:
            refuse("%s sha256 changed during the embedding (%s -> %s)" % (k, s, now))
    print("%s S0's pins re-checked after: unchanged %s" % (TAG, {k: v[:16] for k, v in sha.items()}))


def _read_blobs(path, texts):
    con = RO.open_ro(path)
    try:
        out = {}
        for t in texts:
            r = con.execute("SELECT vector FROM embeddings WHERE query = ?", (t,)).fetchone()
            if r is None:
                refuse("%s holds no vector for a preflight text (sha256 %s)" % (path, hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]))
            out[t] = np.frombuffer(r[0], dtype=">f4").astype(np.float64)
        return out
    finally:
        con.close()


def _cos(a, b, d):
    a, b = np.asarray(a, dtype=np.float64)[:d], np.asarray(b, dtype=np.float64)[:d]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _check_vecs(vs, n):
    if len(vs) != n:
        refuse("the Q8 tag returned %d vectors for %d texts" % (len(vs), n))
    for v in vs:
        a = np.asarray(v, dtype=np.float64)
        if a.shape != (NATIVE,):
            refuse("the Q8 tag returned a %d-d vector (native %d)" % (a.size, NATIVE))
        if not np.all(np.isfinite(a)) or not np.linalg.norm(a) > 0:
            refuse("the Q8 tag returned a non-finite or zero vector")


def preflight(texts, emb_dir, embed_fn, digest_fn, stored=()):
    """T1-T4 (docstring); stored = the Q8 file's texts as read by the caller's state check (T4 compares those rows). -> (the Q8 tag's
    digest, {d: list of cos(Q8, Q4)})."""
    print("%s Ollama endpoint %s (resolved from OLLAMA_HOST=%r by embedder_arms.client_base)" % (TAG, EA.OLLAMA_URL, os.environ.get("OLLAMA_HOST")))
    dq8, dq4 = digest_fn(MODEL_Q8), digest_fn(MODEL_Q4)
    print("%s T1 /api/tags: %s digest %s; %s digest %s" % (TAG, MODEL_Q8, dq8, MODEL_Q4, dq4))
    if not dq8:
        refuse("T1: %s is not listed by /api/tags (pull incomplete or absent): nothing is posted" % MODEL_Q8)
    if dq4 and dq8 == dq4:
        refuse("T1: %s and %s carry the same digest %s: the same weights, nothing to compare" % (MODEL_Q8, MODEL_Q4, dq8))
    chosen = texts[:PARITY_N]
    q4 = _read_blobs(ITS.emb_path("qwen3", emb_dir), chosen)
    v1 = embed_fn(MODEL_Q8, chosen)
    _check_vecs(v1, len(chosen))
    cos = {d: [_cos(a, q4[t], d) for t, a in zip(chosen, v1)] for d in COS_SLICES}
    for d in COS_SLICES:
        print("%s T2 cos(Q8, Q4) on %d texts (S0 text set, first %d by sha256), slice %d + renormalise: min %.6f median %.6f "
              "(different models: PRINTED, NO BAR)" % (TAG, len(chosen), PARITY_N, d, min(cos[d]), float(np.median(cos[d]))))
    v2 = embed_fn(MODEL_Q8, chosen)
    _check_vecs(v2, len(chosen))
    rep = [_cos(a, b, EA.PARITY_SLICE) for a, b in zip(v1, v2)]
    print("%s T3 repeatability %s: %d texts posted twice, cos after slice-%d + renormalise min %.6f median %.6f (bar >= %.4f): %s"
          % (TAG, MODEL_Q8, len(rep), EA.PARITY_SLICE, min(rep), float(np.median(rep)), SELF_BAR, "PASS" if min(rep) >= SELF_BAR else "FAIL"))
    if not min(rep) >= SELF_BAR:
        refuse("T3: repeatability min cos %.6f < %.4f" % (min(rep), SELF_BAR))
    p = q8_path(emb_dir)
    have = sorted(stored, key=lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest())
    if len(have) >= PARITY_N:
        stored = _read_blobs(p, have[:PARITY_N])
        new = embed_fn(MODEL_Q8, have[:PARITY_N])
        _check_vecs(new, PARITY_N)
        par = [_cos(stored[t], v, EA.PARITY_SLICE) for t, v in zip(have[:PARITY_N], new)]
        print("%s T4 resume parity %s: %d stored rows re-embedded, cos after slice-%d + renormalise min %.6f median %.6f (bar >= %.4f): %s"
              % (TAG, os.path.basename(p), len(par), EA.PARITY_SLICE, min(par), float(np.median(par)), SELF_BAR,
                 "PASS" if min(par) >= SELF_BAR else "FAIL"))
        if not min(par) >= SELF_BAR:
            refuse("T4: resume parity min cos %.6f < %.4f" % (min(par), SELF_BAR))
    else:
        print("%s T4 resume parity: %d stored rows in %s (< %d): first launch, nothing to compare" % (TAG, len(have), os.path.basename(p), PARITY_N))
    return dq8, cos


def timed_probe(texts, embed_fn, n_todo, n=PROBE_N):
    sub = texts[:n]
    t0 = time.perf_counter()
    for s in range(0, len(sub), EA.BATCH):
        embed_fn(MODEL_Q8, sub[s:s + EA.BATCH])
    dt = max(time.perf_counter() - t0, 1e-9)
    rate = len(sub) / dt
    print("%s PRICE %s: timed probe %d texts in %.1f s = %.1f texts/s -> %d texts to embed = %.1f min (estimate from the probe)"
          % (TAG, MODEL_Q8, len(sub), dt, rate, n_todo, n_todo / rate / 60.0))
    return rate


def _state(path, want):
    if os.path.exists(path):
        ITS.check_meta(path, want)
        return True, ITS.present_texts(path)
    return False, set()


def dry_run(db=None, emb_dir=None, embed_fn=None, digest_fn=None, probe_n=PROBE_N):
    db, emb_dir = db or II.DEFAULT_OUT, emb_dir or ITS.DATA_ROOT
    embed_fn, digest_fn = embed_fn or EA.ollama_embed, digest_fn or EA.model_digest
    print("%s zero judge calls; DRY RUN: nothing written; the preflight and the probe POST embeddings (Ollama), nothing else" % TAG)
    ITS.check_emb_dir(emb_dir)
    path = q8_path(emb_dir)
    ITS.check_emb_target(path)
    sha, texts, set_sha = load_inputs(db, emb_dir)
    want = expected_meta_q8(set_sha, len(texts), sha["ingest_db"])
    exists, have = _state(path, want)
    todo = sum(1 for t in texts if t not in have)
    print("%s text set %d texts sha256 %s; %s %s: %d present, %d to embed" % (TAG, len(texts), set_sha, os.path.basename(path),
                                                                               "exists (RESUME)" if exists else "absent (new)", len(have), todo))
    heavy_check()
    disk_line(emb_dir, "dry-run")
    with q8_registered():
        preflight(texts, emb_dir, embed_fn, digest_fn, stored=have)
        timed_probe(texts, embed_fn, todo, n=probe_n)
    print("%s TRANSPORT PREFLIGHT PASSED (T1-T4)" % TAG)
    after_check(sha, db, emb_dir)
    print("%s dry: nothing written" % TAG)
    return 0


def embed(go, limit=None, db=None, emb_dir=None, embed_fn=None, digest_fn=None):
    db, emb_dir = db or II.DEFAULT_OUT, emb_dir or ITS.DATA_ROOT
    embed_fn, digest_fn = embed_fn or EA.ollama_embed, digest_fn or EA.model_digest
    ITS.check_emb_dir(emb_dir)
    path = q8_path(emb_dir)
    ITS.check_emb_target(path)
    sha, texts, set_sha = load_inputs(db, emb_dir)
    want = expected_meta_q8(set_sha, len(texts), sha["ingest_db"])
    exists, have = _state(path, want)
    miss = [t for t in texts if t not in have]
    todo = miss if limit is None else [t for t in texts[:int(limit)] if t not in have]
    print("%s embed %s (%s, RAW) -> %s (%s): text set %d (sha256 %s), present %d, missing %d, this launch %d%s"
          % (TAG, E_Q8, MODEL_Q8, path, "exists: RESUME" if exists else "new", len(texts), set_sha[:16], len(have), len(miss), len(todo),
             "" if limit is None else " (--limit %d)" % int(limit)))
    if not go:
        print("%s dry: nothing posted, nothing written (add --go)" % TAG)
        return 0
    heavy_check()
    disk_line(emb_dir, "before")
    before = ITS.record_table_hashes()
    print("%s shared caches per-table before: %s" % (TAG, json.dumps(before, sort_keys=True)))
    with q8_registered():
        digest, _cos = preflight(texts, emb_dir, embed_fn, digest_fn, stored=have)
        if not exists:
            with open(path, "xb"):                        # exclusive create: a file that appeared meanwhile is never overwritten
                pass
            con = sqlite3.connect(path)
            try:
                con.execute("PRAGMA journal_mode=DELETE")
                con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
                con.executemany("INSERT INTO intent_meta VALUES (?, ?)", sorted(dict(want, model_digest=digest).items()))
                con.commit()
            finally:
                con.close()
        else:
            ITS.check_meta(path, want, digest=digest)
        n = EA.write_vectors(path, ARM_Q8, todo, embed_fn) if todo else 0
    after = ITS.record_table_hashes()
    if after != before:
        refuse("the shared caches' per-table hashes CHANGED during the embedding: before %s after %s" % (before, after))
    print("%s shared caches per-table after: unchanged" % TAG)
    after_check(sha, db, emb_dir)
    disk_line(emb_dir, "after")
    left = len(miss) - n
    print("%s embed %s: wrote %d; %d of the set still missing%s" % (TAG, E_Q8, n, left, "" if left else " (COMPLETE)"))
    return n


# ------------------------------------------------------------------------------------------------ selftest
def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    got = [ln[len(TAG) + 1:] for ln in out.splitlines() if ln.startswith(TAG + " " + prefix)]
    return got[-1] if got else ""


class Stub(object):
    """In-process embed_fn / digest_fn: Q8 vectors = the text's stored Q4 vector + a deterministic perturbation of scale `eps` (so
    cos(Q8, Q4) is known), optionally a per-call jitter (repeatability), a wrong dimension or a zero vector."""

    def __init__(self, q4, eps=0.02, jitter=0.0, dim=NATIVE, zero=False, digests=None):
        self.q4, self.eps, self.jitter, self.dim, self.zero = q4, eps, jitter, dim, zero
        self.calls, self.n = [], 0
        self.digests = {MODEL_Q8: "sha256:q8", MODEL_Q4: "sha256:q4"} if digests is None else digests

    def vec(self, t, call):
        base = self.q4[t] if t in self.q4 else np.ones(NATIVE)
        r = np.random.default_rng(int(hashlib.sha256(("q8" + t).encode("utf-8")).hexdigest()[:8], 16))
        v = base + self.eps * np.linalg.norm(base) / np.sqrt(NATIVE) * r.normal(size=NATIVE)
        if self.jitter:
            rj = np.random.default_rng(call * 7919 + int(hashlib.sha256(t.encode("utf-8")).hexdigest()[:6], 16))
            v = v + self.jitter * np.linalg.norm(base) / np.sqrt(NATIVE) * rj.normal(size=NATIVE)
        if self.zero:
            v = np.zeros(NATIVE)
        return [float(x) for x in v[:self.dim]] + [0.0] * max(0, self.dim - NATIVE)

    def embed(self, model, inputs):
        self.n += 1
        self.calls.append((model, list(inputs)))
        if model != MODEL_Q8:
            raise AssertionError("posted to %s" % model)
        return [self.vec(t, self.n) for t in inputs]

    def digest(self, model, url=None):
        return self.digests.get(model)


def build_fixture(td):
    """S0's own fixture (ingest DB + intent_emb_{qwen3,nomic,gemma}.db, planted 4096-d qwen3) and a pins file for it."""
    with contextlib.redirect_stdout(io.StringIO()):
        db, CS, texts, derived = ITS.build_fixture(td)
    pins = ITS._pins_file(td, db, td)
    con = sqlite3.connect(ITS.emb_path("qwen3", td))
    q4 = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in con.execute("SELECT query, vector FROM embeddings")}
    con.close()
    return {"td": td, "db": db, "pins": pins, "texts": texts, "q4": q4}


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K, the fixture's pins, no heavy process, S0's DATA_ROOT = the fixture directory (so the shared-cache
    hashes read nothing real), Ollama on a closed port (nothing real is contacted); restored on exit."""
    saved = (ITS._foreign_heavy, ITS.PINS_FILE_OVERRIDE[0], EA.OLLAMA_URL, ITS.DATA_ROOT)
    ITS._foreign_heavy = lambda: []
    EA.OLLAMA_URL = "http://127.0.0.1:9/api/embed"
    ITS.DATA_ROOT = fx.get("emb_dir") or fx.get("td") or tempfile.gettempdir()
    with ITS.fixture_scope():
        ITS.PINS_FILE_OVERRIDE[0] = fx["pins"]
        try:
            yield
        finally:
            ITS._foreign_heavy, ITS.PINS_FILE_OVERRIDE[0], EA.OLLAMA_URL, ITS.DATA_ROOT = saved


def _fresh(fx, name):
    d = os.path.join(fx["td"], name)
    os.makedirs(d)
    for f in (II.DB_NAME, "intent_emb_qwen3.db"):
        shutil.copyfile(os.path.join(fx["td"], f), os.path.join(d, f))
    return dict(fx, emb_dir=d, db=os.path.join(d, II.DB_NAME))


def _rows(path):
    con = sqlite3.connect(path)
    try:
        return {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in con.execute("SELECT query, vector FROM embeddings")}, \
            dict(con.execute("SELECT key, value FROM intent_meta"))
    finally:
        con.close()


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    td = None
    try:
        if fixture is None:
            td = tempfile.mkdtemp(prefix="eqw_st_")
            with _scope({"pins": None}):
                fixture = build_fixture(td)
        _selftest(sel, ok, fixture)
    finally:
        if td:
            shutil.rmtree(td, ignore_errors=True)
    if not quiet:
        print("SELFTEST (writer): %d checks passed" % n[0])
    return 0


def _selftest(sel, ok, fx):
    if sel("W-CONST"):
        ok(check_its_blob() == ITS_BLOB, "W-CONST intent_transfer_s0.py is blob f662ceb (imported unchanged)")
        ok((MODEL_Q8, MODEL_Q4, E_Q8, NATIVE, QUANT) == ("qwen3-embedding:8b-q8_0", "qwen3-embedding:latest", "qwen3_q8", 4096, "Q8_0"),
           "W-CONST tag qwen3-embedding:8b-q8_0 vs qwen3-embedding:latest, arm qwen3_q8, 4096-d, Q8_0")
        ok(ARM_Q8.prefix == "" and ARM_Q8.layer_norm is False and ARM_Q8.role == "PRIMARY", "W-CONST RAW protocol (no prefix, no transform)")
        ok(os.path.basename(q8_path("x")) == "intent_emb_qwen3_q8.db", "W-CONST file intent_emb_qwen3_q8.db")
        ok((PARITY_N, SELF_BAR, COS_SLICES) == (20, 0.998, (256, 1024, 4096)), "W-CONST 20 texts, repeatability bar 0.998, cos at 256/1024/4096")
    if sel("W-REG"):
        ok(MODEL_Q8 not in EA.EG.NATIVE_DIM and E_Q8 not in ITS.MODEL, "W-REG the tag is unknown outside q8_registered()")
        with q8_registered():
            ok(EA.EG.NATIVE_DIM[MODEL_Q8] == 4096 and ITS.MODEL[E_Q8] == MODEL_Q8, "W-REG registered inside")
        ok(MODEL_Q8 not in EA.EG.NATIVE_DIM and E_Q8 not in ITS.MODEL, "W-REG removed again after the call")
        try:
            with q8_registered():
                raise KeyError("x")
        except KeyError:
            pass
        ok(MODEL_Q8 not in EA.EG.NATIVE_DIM and E_Q8 not in ITS.MODEL, "W-REG removed after an exception too")
    if sel("W-GO"):
        f = _fresh(fx, "go")
        st = Stub(fx["q4"], eps=0.05)
        with _scope(f):
            o, err, res = _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err is None, "W-GO --embed --go completes on the fixture (%s)" % err)
        path = q8_path(f["emb_dir"])
        rows, meta = _rows(path)
        ok(set(rows) == set(fx["texts"]) and res == len(fx["texts"]), "W-GO every text of S0's set written (%d of %d)" % (len(rows), len(fx["texts"])))
        t0 = fx["texts"][5]
        ok(np.allclose(rows[t0], np.asarray(st.vec(t0, 0), dtype=">f4").astype(np.float64)), "W-GO stored vector = the tag's vector (RAW, big-endian f4)")
        ok(all(len(v) == 4096 for v in rows.values()), "W-GO every stored vector 4096-d")
        ok(meta["model"] == MODEL_Q8 and meta["embedder"] == E_Q8 and meta["quant"] == "Q8_0" and meta["protocol"] == "RAW"
           and meta["model_digest"] == "sha256:q8" and meta.get("writer_blob_lf") == writer_blob() and meta["script_blob_lf"] == ITS_BLOB,
           "W-GO intent_meta: model, embedder, quant, protocol, digest, writer blob, S0 blob")
        set_sha = ITS.text_set(ITS.load_corpora(f["db"]))[1]
        ok(meta["text_set_sha256"] == set_sha and meta["n_texts"] == str(len(fx["texts"])), "W-GO intent_meta pins S0's text set and count")
        ok("(COMPLETE)" in _line(o, "embed qwen3_q8: wrote"), "W-GO prints COMPLETE")
        ok(all(m == MODEL_Q8 for m, _i in st.calls), "W-GO every POST names the Q8 tag (%d posts)" % len(st.calls))
        ok(st.calls[0][1] == fx["texts"][:20] and st.calls[1][1] == fx["texts"][:20], "W-GO preflight posts the first 20 texts twice (T2, T3)")
        exp = sorted(_cos(st.vec(t, 0), fx["q4"][t], 1024) for t in fx["texts"][:20])
        ln = _line(o, "T2 cos(Q8, Q4) on 20 texts (S0 text set, first 20 by sha256), slice 1024")
        ok(("min %.6f median %.6f" % (exp[0], float(np.median(exp)))) in ln and "NO BAR" in ln,
           "W-GO T2 prints min / median cos(Q8, Q4) at 1024 = an independent recomputation (%.6f / %.6f)" % (exp[0], float(np.median(exp))))
        exp4 = sorted(_cos(st.vec(t, 0), fx["q4"][t], 4096) for t in fx["texts"][:20])
        ok(("min %.6f" % exp4[0]) in _line(o, "T2 cos(Q8, Q4) on 20 texts (S0 text set, first 20 by sha256), slice 4096"), "W-GO T2 slice 4096 value")
        ok("first launch" in _line(o, "T4"), "W-GO T4 first launch: nothing to compare")
        gb = shutil.disk_usage(f["emb_dir"]).free / 1e9
        dl = [float(_line(o, "DISK %s" % w).split(": ")[1].split(" GB")[0]) for w in ("before", "after")]
        ok(all(abs(x - gb) < 1.0 for x in dl), "W-GO DISK before / after printed in GB (%.2f / %.2f; now %.2f)" % (dl[0], dl[1], gb))
        ok(MODEL_Q8 not in EA.EG.NATIVE_DIM, "W-GO registration removed after --go")
        # resume: a partial file continues; T4 compares stored rows
        f2 = _fresh(fx, "resume")
        st2 = Stub(fx["q4"], eps=0.05)
        with _scope(f2):
            _cap(lambda: embed(True, limit=40, db=f2["db"], emb_dir=f2["emb_dir"], embed_fn=st2.embed, digest_fn=st2.digest))
            n40 = len(_rows(q8_path(f2["emb_dir"]))[0])
            o2, err2, res2 = _cap(lambda: embed(True, db=f2["db"], emb_dir=f2["emb_dir"], embed_fn=st2.embed, digest_fn=st2.digest))
        ok(n40 == 40 and err2 is None and res2 == len(fx["texts"]) - 40, "W-GO --limit 40 then resume: 40 then the remaining %d" % (len(fx["texts"]) - 40))
        ok("PASS" in _line(o2, "T4 resume parity") and "min 1.000000" in _line(o2, "T4 resume parity"), "W-GO T4 resume parity PASS at min 1.000000")
    if sel("W-REFUSE"):
        def go(name, st, pre=None, **kw):
            f = _fresh(fx, name)
            if pre:
                pre(f)
            with _scope(f):
                o, err, _r = _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, **kw))
            return o, err, f
        o, err, f = go("unlisted", Stub(fx["q4"], digests={MODEL_Q4: "sha256:q4"}))
        ok(err and "T1" in err and "not listed" in err and not os.path.exists(q8_path(f["emb_dir"])), "W-REFUSE T1 tag not listed (pull pending): refused, no file")
        o, err, f = go("samedigest", Stub(fx["q4"], digests={MODEL_Q8: "d", MODEL_Q4: "d"}))
        ok(err and "same digest" in err and not os.path.exists(q8_path(f["emb_dir"])), "W-REFUSE T1 same digest as Q4: refused")
        o, err, f = go("wrongdim", Stub(fx["q4"], dim=1024))
        ok(err and "1024-d" in err and not os.path.exists(q8_path(f["emb_dir"])), "W-REFUSE T2 a 1024-d vector: refused, no file")
        o, err, f = go("zero", Stub(fx["q4"], zero=True))
        ok(err and "zero vector" in err, "W-REFUSE T2 a zero vector: refused")
        o, err, f = go("jitter", Stub(fx["q4"], jitter=0.2))
        ok(err and "T3" in err and not os.path.exists(q8_path(f["emb_dir"])), "W-REFUSE T3 repeatability below 0.998: refused, no file")
        st_ok = Stub(fx["q4"], jitter=0.01)
        o, err, f = go("jitter_small", st_ok, limit=25)
        ok(err is None and "PASS" in _line(o, "T3"), "W-REFUSE T3 small jitter passes (both branches executed)")

        def tamper(f):
            st = Stub(fx["q4"])
            with _scope(f):
                _cap(lambda: embed(True, limit=40, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
            p = q8_path(f["emb_dir"])
            con = sqlite3.connect(p)
            for t, in con.execute("SELECT query FROM embeddings").fetchall():
                con.execute("UPDATE embeddings SET vector = ? WHERE query = ?", (np.asarray(-fx["q4"][t], dtype=">f4").tobytes(), t))
            con.commit()
            con.close()
        o, err, f = go("t4", Stub(fx["q4"]), pre=tamper)
        ok(err and "T4" in err, "W-REFUSE T4 stored rows that the tag no longer reproduces: refused")

        def redigest(f):
            st = Stub(fx["q4"])
            with _scope(f):
                _cap(lambda: embed(True, limit=40, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        o, err, f = go("redigest", Stub(fx["q4"], digests={MODEL_Q8: "sha256:REPULLED", MODEL_Q4: "sha256:q4"}), pre=redigest)
        ok(err and "model_digest" in err, "W-REFUSE a re-pulled tag (other digest) never resumes the file")

        def remeta(f):
            redigest(f)
            con = sqlite3.connect(q8_path(f["emb_dir"]))
            con.execute("UPDATE intent_meta SET value = 'x' WHERE key = 'writer_blob_lf'")
            con.commit()
            con.close()
        o, err, f = go("remeta", Stub(fx["q4"]), pre=remeta)
        ok(err and "writer_blob_lf" in err, "W-REFUSE a file started under another writer blob is never resumed")

        f = _fresh(fx, "race")
        st = Stub(fx["q4"])
        racer = {"p": q8_path(f["emb_dir"])}

        def racing_digest(model, url=None):          # the file appears between the state read and the exclusive create
            if not os.path.exists(racer["p"]):
                open(racer["p"], "wb").close()
            return st.digest(model)
        raced = None
        with _scope(f):
            try:
                _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=racing_digest))
            except FileExistsError as ex:
                raced = ex
        ok(raced is not None and os.path.getsize(racer["p"]) == 0, "W-REFUSE a file that appears before the first write is never written (exclusive create)")
        f = _fresh(fx, "heavy")
        st = Stub(fx["q4"])
        with _scope(f):
            ITS._foreign_heavy = lambda: ['"java.exe","123"']
            o, err, _r = _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "heavy" in err and st.n == 0, "W-REFUSE a java.exe running: refused before any POST")
        f = _fresh(fx, "pinbad")
        bad = os.path.join(f["emb_dir"], "pins_bad.json")
        p = json.load(open(fx["pins"]))
        p["emb"]["qwen3"] = "0" * 64
        json.dump(p, open(bad, "w"))
        st = Stub(fx["q4"])
        with _scope(f):
            ITS.PINS_FILE_OVERRIDE[0] = bad
            o, err, _r = _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "intent_emb_qwen3.db" in err and st.n == 0, "W-REFUSE the Q4 file off its S0 pin: refused before any POST")
        p["emb"]["qwen3"] = None
        json.dump(p, open(bad, "w"))
        with _scope(f):
            ITS.PINS_FILE_OVERRIDE[0] = bad
            o, err, _r = _cap(lambda: embed(True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "UNPINNED" in err, "W-REFUSE an unpinned Q4 file: refused (S0's pins strict)")
        f = _fresh(fx, "nogo")
        st = Stub(fx["q4"])
        with _scope(f):
            o, err, r = _cap(lambda: embed(False, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err is None and r == 0 and st.n == 0 and not os.path.exists(q8_path(f["emb_dir"])), "W-REFUSE without --go: nothing posted, nothing written")
    if sel("W-DRY"):
        f = _fresh(fx, "dry")
        st = Stub(fx["q4"], eps=0.05)
        with _scope(f):
            o, err, r = _cap(lambda: dry_run(db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, probe_n=64))
        ok(err is None and "TRANSPORT PREFLIGHT PASSED" in o and not os.path.exists(q8_path(f["emb_dir"])), "W-DRY preflight passes, nothing written")
        ok(("%d to embed" % len(fx["texts"])) in _line(o, "text set") and "PRICE" in o and st.calls[-1][1] == fx["texts"][32:64],
           "W-DRY counts %d to embed and prices with a timed probe of 64 texts" % len(fx["texts"]))
        st = Stub(fx["q4"], digests={})
        with _scope(f):
            o, err, r = _cap(lambda: dry_run(db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, probe_n=64))
        ok(err and "not listed" in err and "PASSED" not in o, "W-DRY an unlisted tag fails the dry-run's preflight")
    if sel("W-HTTP"):
        # the real ollama_embed / model_digest path against embedder_arms' stub Ollama (127.0.0.1, ephemeral port; nothing real)
        f = _fresh(fx, "http")
        with _scope(f):
            with q8_registered():
                with EA.stub_ollama() as (url, log, state):
                    EA.OLLAMA_URL = url
                    o, err, r = _cap(lambda: embed(True, limit=40, db=f["db"], emb_dir=f["emb_dir"]))
        rows, meta = _rows(q8_path(f["emb_dir"]))
        ok(err is None and len(rows) == 40 and meta["model_digest"] == "stubdigest-" + MODEL_Q8,
           "W-HTTP through ollama_embed + /api/tags on the stub server: 40 rows, digest stubdigest-%s (%s)" % (MODEL_Q8, err))
        ok(all(m == MODEL_Q8 for _p, m, _i in log) and len(log) >= 4, "W-HTTP every request names the Q8 tag (%d requests)" % len(log))


MUTANTS = (
    ("T2 posts the Q4 tag", "    v1 = embed_fn(MODEL_Q8, chosen)\n", "    v1 = embed_fn(MODEL_Q4, chosen)\n", ("W-GO",)),
    ("write_vectors with the Q4 arm", "        n = EA.write_vectors(path, ARM_Q8, todo, embed_fn)", "        n = EA.write_vectors(path, EA.ARMS['qwen3_raw'], todo, embed_fn)", ("W-GO",)),
    ("T1 unlisted tag admitted", "    if not dq8:\n        refuse(", "    if False:\n        refuse(", ("W-REFUSE", "W-DRY")),
    ("T1 same digest admitted", "    if dq4 and dq8 == dq4:\n", "    if False:\n", ("W-REFUSE",)),
    ("T3 bar dropped", "    if not min(rep) >= SELF_BAR:\n", "    if False:\n", ("W-REFUSE",)),
    ("T3 bar 0.9", "SELF_BAR = ITS.PARITY_BAR[\"qwen3\"]\n", "SELF_BAR = 0.9\n", ("W-CONST", "W-REFUSE")),
    ("T4 skipped on resume", "    if len(have) >= PARITY_N:\n", "    if False:\n", ("W-REFUSE", "W-GO")),
    ("T2 cos on the median text only (min = max)", "              \"(different models: PRINTED, NO BAR)\" % (TAG, len(chosen), PARITY_N, d, min(cos[d]),",
     "              \"(different models: PRINTED, NO BAR)\" % (TAG, len(chosen), PARITY_N, d, max(cos[d]),", ("W-GO",)),
    ("cos without renormalisation", "    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))\n", "    return float(np.dot(a, b))\n", ("W-GO",)),
    ("dimension check removed", "        if a.shape != (NATIVE,):\n", "        if False:\n", ("W-REFUSE",)),
    ("zero-vector check removed", "        if not np.all(np.isfinite(a)) or not np.linalg.norm(a) > 0:\n", "        if False:\n", ("W-REFUSE",)),
    ("first launch not exclusive", "            with open(path, \"xb\"):", "            with open(path, \"ab\"):", ("W-REFUSE",)),
    ("meta without the writer blob", ", \"writer_blob_lf\": writer_blob()})\n", "})\n", ("W-GO", "W-REFUSE")),
    ("meta digest not checked on resume", "            ITS.check_meta(path, want, digest=digest)\n", "            ITS.check_meta(path, want)\n", ("W-REFUSE",)),
    ("S0 pins not strict", "    sha[\"qwen3\"] = ITS.pin_check(q4, \"emb\", True,", "    sha[\"qwen3\"] = ITS.pin_check(q4, \"emb\", False,", ("W-REFUSE",)),
    ("Q4 pin not checked", "    sha[\"qwen3\"] = ITS.pin_check(q4, \"emb\", True, sub=\"qwen3\", label=\"intent_emb_qwen3.db\")\n",
     "    sha[\"qwen3\"] = II.file_sha(q4)\n", ("W-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("W-REFUSE",)),
    ("registration not removed", "        if add_dim:\n            EA.EG.NATIVE_DIM.pop(MODEL_Q8, None)\n", "        pass\n", ("W-REG",)),
    ("--limit ignored", "    todo = miss if limit is None else", "    todo = miss if True else", ("W-GO",)),
    ("go flag ignored", "    if not go:\n        print(\"%s dry: nothing posted", "    if False:\n        print(\"%s dry: nothing posted", ("W-REFUSE",)),
    ("preflight texts = the last 20", "    chosen = texts[:PARITY_N]\n", "    chosen = texts[-PARITY_N:]\n", ("W-GO",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="eqw_mut_")
    with _scope({"pins": None}):
        fx = build_fixture(td)
    killed, rows = 0, []
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        code = head.replace(old, new)
        ns = {"__name__": "eqw_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=None if tests is None else set(tests), quiet=True, fixture=fx)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        finally:
            EA.EG.NATIVE_DIM.pop(MODEL_Q8, None)
            ITS.MODEL.pop(E_Q8, None)
            for d in os.listdir(td):
                if os.path.isdir(os.path.join(td, d)):
                    shutil.rmtree(os.path.join(td, d), ignore_errors=True)
        killed += res.startswith("KILLED")
        rows.append((name, res))
        print("  %-48s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS (writer): %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="EMBED-QUANT writer: qwen3-embedding:8b-q8_0 over S0's text set (zero judge calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--embed", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--db", default=None)
    ap.add_argument("--emb-dir", default=None)
    ap.add_argument("--probe-n", type=int, default=PROBE_N)
    ap.add_argument("--pace-s", type=float, default=None, help="--embed only: pause S seconds after each committed batch")
    ap.add_argument("--tw-drain", type=int, default=None, help="--embed only: after a transient error, wait for TIME_WAIT < N")
    a = ap.parse_args(argv)
    if (a.pace_s is not None or a.tw_drain is not None) and not a.embed:
        refuse("--pace-s / --tw-drain are admitted with --embed only")
    if (a.pace_s is not None and not a.pace_s > 0) or (a.tw_drain is not None and a.tw_drain < 1):
        refuse("--pace-s must be > 0 and --tw-drain >= 1 (got %r / %r)" % (a.pace_s, a.tw_drain))
    if (a.go or a.limit is not None) and not a.embed:
        refuse("--go / --limit are admitted with --embed only")
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.db, a.emb_dir, probe_n=a.probe_n)
    saved = (EA.PACE_S, EA.TW_DRAIN)
    if a.pace_s is not None or a.tw_drain is not None:
        EA.PACE_S = a.pace_s if a.pace_s is not None else EA.PACE_S
        EA.TW_DRAIN = a.tw_drain if a.tw_drain is not None else EA.TW_DRAIN
        print("%s pacing: pause %s s after each batch; TIME_WAIT drain threshold %s (poll %.0f s, cap %.0f s)"
              % (TAG, EA.PACE_S or "none", EA.TW_DRAIN, EA.TW_POLL_S, EA.TW_MAX_S))
    try:
        embed(a.go, limit=a.limit, db=a.db, emb_dir=a.emb_dir)
    finally:
        EA.PACE_S, EA.TW_DRAIN = saved
    return 0


if __name__ == "__main__":
    sys.exit(main())
