"""INTENT-S0-CARD-PROTOCOL writer: re-embeds S0's text set (57,350 texts) with each embedder's CARD prompt into its own DB.

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — INTENT-S0-CARD-PROTOCOL: at
each embedder's EMBED-DIM-SLICE-selected slice, does gemma's fine-level edge over qwen3 survive card-conformant prompts on both sides
(CP1), and do card prompts raise qwen3's fine NMI over RAW (CP2)? (zero calls; Ollama re-embedding; no build)", span L22655-L22680
_as_of 46954215 (drafted in docs/agents/plans/2026-10-02_next_registrations.md section 3, ce0d0f17). PROMPT ARM ONLY (the dimension
arm is EMBED-DIM-SLICE). This writer posts EMBEDDINGS only (Ollama /api/embed), never a judge call.

THE REGISTERED PROMPT STRINGS (quoted; "PROMPT STRINGS (exact bytes, UTF-8; prepended to EVERY text of every side: TRAIN, GATE,
EVAL, variants, OOS; committed before any embedding in experiment_configs/card_protocol_prompts.json, whose sha256 the READY pins)"):
  qwen3  "Instruct: Given a user utterance to a virtual assistant, identify the user's intent\\nQuery:" + text  (\\n = ONE LF byte,
         no space after "Query:"; one task line for all three corpora, not tuned per corpus)
  gemma  "task: clustering | query: " + text
  nomic  "clustering: " + text            (DESCRIPTIVE arm CP4)
The strings live in experiment_configs/card_protocol_prompts.json (sha256 of the LF rendering PROMPTS_FILE_SHA, pinned below) AND as
constants here; load_prompts() REFUSES unless the file's sha256 is the pin and every file value equals its constant byte for byte
(double entry: neither a file edit nor a code edit can change a prompt silently). Each string's own sha256 is printed and stored.

WHY A SEPARATE SCRIPT (the EMBED-QUANT pattern, QB1 of READY_embed_quant). tools/analysis/intent_transfer_s0.py
(blob:f662ceb19738f515972871f5963f5dcfc764a271, asserted at every entry point) and tools/analysis/embedder_arms.py are imported
UNCHANGED: their blobs are pinned in the intent_meta of S0's three RAW DBs, so a flag on either would orphan them. S0 (ITS) does
every read and the text set: pin_check / raw_pin_check (strict), load_corpora, text_set (sha256-ordered), check_emb_dir /
check_emb_target (no cache of record, nothing under experiment_results/, a non-empty -wal / -journal REFUSES), check_meta /
present_texts, record_table_hashes (the shared caches' per-table hashes before and after), _foreign_heavy. embedder_arms (EA) does
every POST and every write: ollama_embed (one keep-alive connection, bounded whole-batch retry, EMB-CONN), write_vectors (posts
arm.prefix + text, stores under the RAW text, INSERT OR IGNORE, commit per batch: resumable), model_digest (/api/tags), and the
EMB-PACE flags --pace-s / --tw-drain (off by default).

THE ARMS. embedder e in {qwen3, gemma, nomic}: model = S0's model for e (qwen3-embedding:latest = the Q4_K_M tag of S0's RAW arm;
embeddinggemma:latest; nomic-embed-text:latest), protocol CARD, prefix = the registered string, NO transform (layer_norm off: the
registration prepends a prompt and nothing else; reading CW1), file intent_emb_<e>_card.db under --emb-dir (default DATA_ROOT =
TAXOARENA_DATA_ROOT or the repo root; root *.db are gitignored).

FILE PINS (intent_meta, first launch, exclusive create "xb"): S0's expected_meta fields for e (text-set sha256 and count, ingest DB
sha256, S0's blob, embedder_arms' blob, native dim, model) with embedder "<e>_card", protocol CARD, prompt (the string),
prompt_sha256, prompts_file_sha256, writer_blob_lf (this file's LF blob), and model_digest. A later launch RESUMES only under identical
pins (another prompt, writer blob, text set or digest REFUSES; such a file is discarded, never re-pinned).

TRANSPORT PREFLIGHT (inside --dry-run, and before any --embed --go write); zero judge calls:
  T0 prompts: the file's sha256 and every string checked (above); printed with each string's sha256 and repr.
  T1 /api/tags: the tag must be listed with a digest, and the digest must EQUAL the model_digest stored in S0's RAW file for e (the
     CARD arm must be the very weights of the RAW arm it is compared with in CP2 / CP4); else REFUSES, nothing posted.
  T2 RAW route parity (the registration's "checks route parity (S0's bars: qwen3 0.9980, gemma 0.9999)"): the first PARITY_N = 20
     texts of the set (sha256 order) posted WITHOUT a prefix, compared with S0's pinned RAW vectors after slice 256 + renormalise;
     min cos >= ITS.PARITY_BAR[e] (qwen3 0.998, gemma 0.9999, nomic 0.9999) else REFUSES.
  T2b the same 20 texts posted WITH the card prefix: every vector native-d, finite, non-zero (else REFUSES); cos(CARD, RAW) against
     S0's stored RAW vectors after slice d + renormalise, d in COS_SLICES[e], min and median PRINTED, NO BAR (the orchestrator's
     brief; the prompt is the treatment, so no parity is defined between the protocols).
  T3 repeatability: the 20 card inputs posted again; min cos(first, second) after slice 256 + renormalise >= PARITY_BAR[e] else
     REFUSES.
  T4 resume parity: when the card file already holds rows, the first min(20, rows) STORED rows (sha256 order) are re-embedded WITH
     the prefix and compared with the stored vectors (slice 256, >= PARITY_BAR[e]) else REFUSES. Unlike EMBED-QUANT's writer (READY
     D3), a file with 1-19 rows is checked too (all of its rows).
  --dry-run adds a timed probe (PROBE_N = 500 texts posted with the prefix, nothing written) and prices the pass; disk free printed.

HYGIENE (the registration's HYGIENE line): embeddings_cache.db and S0's three pinned DBs are never written; S0's ingest DB and RAW DB
for e are sha256-checked before (strict pins) and after the pass (a change REFUSES), and the shared caches' per-table hashes before
and after (a change REFUSES). A non-empty -wal / -journal beside the target REFUSES before any POST, whether or not the target exists
(READY_embed_quant D1 / OM5: checked by this script itself, first, not left to sqlite's open). Ollama is one heavy process: a
running java.exe REFUSES (the guard sees java only: the operator keeps Ollama serving this pass alone).

LAUNCH (run-operator; zero judge calls; serial in the Ollama lane; one embedder per invocation):
  python tools/analysis/card_protocol_writer.py --selftest
  python tools/analysis/card_protocol_writer.py --mutants
  python tools/analysis/card_protocol_writer.py --dry-run --embedder gemma          # T0-T4, probe price; writes nothing
  python tools/analysis/card_protocol_writer.py --embed --embedder gemma --go       # complete (resumes)
  (then qwen3; nomic, the DESCRIPTIVE arm, last; the registrar pins each COMPLETE file in experiment_configs/card_protocol_pins.json
   from the final "[EMB-ARMS] wrote ... sha256 after" line; tools/analysis/card_protocol.py reads it)

BUILDER'S READINGS (printed by the readout; the registrar confirms or brackets):
  CW1 no transform on any card arm (EA's nomic_card arm layer-norms; the registration prepends a prompt only).
  CW2 T2 applies S0's route-parity bars to the RAW route (same model, same protocol: parity defined); cos(CARD, RAW) printed, no bar.
  CW3 T1 requires the tag's digest to equal S0's RAW file's stored digest (not in the registration's words; it makes CP2's
      CARD - RAW a prompt contrast, not a re-pull contrast).

MUTANT TABLE: `--mutants` runs each mutant against the named selftest sections; the result at build is in the commit message (all
KILLED). Selftest: stubs only (an in-process embed_fn / digest_fn, and embedder_arms' stub Ollama on 127.0.0.1 for the real
ollama_embed / model_digest path); nothing real is contacted and no real DB is read.
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

TAG = "[CARD-W]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
EMB = ("qwen3", "gemma", "nomic")
ROLE = {"qwen3": "DECIDING (CP1, CP2)", "gemma": "DECIDING (CP1)", "nomic": "DESCRIPTIVE (CP4)"}
PROMPTS = {"qwen3": "Instruct: Given a user utterance to a virtual assistant, identify the user's intent\nQuery:",
           "gemma": "task: clustering | query: ",
           "nomic": "clustering: "}
PROMPTS_FILE = os.path.join(ROOT, "experiment_configs", "card_protocol_prompts.json")
PROMPTS_FILE_SHA = "19c3d1f888ba3a99cd4f91f917f3ce47dee41f8f2f8fe7177fe851e71e6e7e76"     # sha256 of the LF rendering
PROMPTS_SCHEMA = "card_protocol_prompts/v1"
PROTOCOL = "CARD"
PARITY_N = 20
COS_SLICES = {"qwen3": (256, 1024, 4096), "gemma": (256, 768), "nomic": (256, 768)}
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


def sha_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def native(e):
    return EA.EG.NATIVE_DIM[ITS.MODEL[e]]


def card_arm(e):
    return EA.Arm(e + "_card", ITS.MODEL[e], PROTOCOL, PROMPTS[e], False)


def card_path(e, emb_dir):
    return ITS.emb_path(e + "_card", emb_dir)


def load_prompts(path=None, want_sha=None):
    """T0: -> the file's LF sha256; REFUSES unless the sha is the pin and every value equals the constant byte for byte."""
    path, want_sha = path or PROMPTS_FILE, want_sha or PROMPTS_FILE_SHA
    if not os.path.isfile(path):
        refuse("T0: the prompts file %s is absent" % path)
    raw = open(path, "rb").read()
    data = raw.replace(b"\r\n", b"\n")
    sha = hashlib.sha256(data).hexdigest()
    print("%s T0 prompts file %s sha256 (LF rendering) %s%s [%s]" % (TAG, os.path.basename(path), sha, "" if raw == data else
                                                                     " (CRLF working-tree sha256 %s)" % hashlib.sha256(raw).hexdigest(),
                                                                     "PIN OK" if sha == want_sha else "PIN MISMATCH"))
    if sha != want_sha:
        refuse("T0: %s sha256 %s != the pinned %s" % (path, sha, want_sha))
    js = json.loads(data.decode("utf-8"))
    if js.get("schema") != PROMPTS_SCHEMA:
        refuse("T0: %s schema %r != %r" % (path, js.get("schema"), PROMPTS_SCHEMA))
    for e in EMB:
        if js.get(e) != PROMPTS[e]:
            refuse("T0: the file's %s prompt %r != the registered constant %r" % (e, js.get(e), PROMPTS[e]))
        print("%s T0 prompt %s [%s]: %r sha256 %s (%d UTF-8 bytes)" % (TAG, e, ROLE[e], PROMPTS[e], sha_text(PROMPTS[e]),
                                                                       len(PROMPTS[e].encode("utf-8"))))
    q = PROMPTS["qwen3"]
    if q.count("\n") != 1 or "\r" in q or not q.endswith("\nQuery:") or not q.startswith("Instruct: "):
        refuse("T0: the qwen3 prompt is not the card form 'Instruct: {task}\\nQuery:' with one LF byte and no space after 'Query:'")
    return sha


def expected_meta_card(e, set_sha, n_texts, ingest_sha, prompts_sha):
    m = ITS.expected_meta(e, set_sha, n_texts, ingest_sha)
    m.update({"embedder": e + "_card", "protocol": PROTOCOL, "prompt": PROMPTS[e], "prompt_sha256": sha_text(PROMPTS[e]),
              "prompts_file_sha256": prompts_sha, "writer_blob_lf": writer_blob()})
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


def target_check(path):
    """READY_embed_quant D1 / OM5: the WAL / journal refusal runs HERE, first, for an absent target too (sqlite's own open would
    discard a bogus -wal before any later check looked). S0's check_emb_target refuses a cache of record and a NON-EMPTY -wal /
    -journal (a 0-byte sidecar is admitted)."""
    ITS.check_emb_target(path)


def load_inputs(e, db, emb_dir):
    """S0's pins (strict) for the ingest DB, its raw files and e's RAW DB; S0's text set; the RAW file's meta. -> (sha, texts, set_sha)."""
    check_its_blob()
    sha = {"ingest_db": ITS.pin_check(db, "ingest_db", True)}
    ITS.raw_pin_check(db, True)
    rp = ITS.emb_path(e, emb_dir)
    sha[e] = ITS.pin_check(rp, "emb", True, sub=e, label="intent_emb_%s.db" % e)
    CS = ITS.load_corpora(db)
    texts, set_sha, _d = ITS.text_set(CS)
    ITS.check_meta(rp, ITS.expected_meta(e, set_sha, len(texts), sha["ingest_db"]))
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
                refuse("%s holds no vector for a preflight text (sha256 %s)" % (path, sha_text(t)[:16]))
            out[t] = np.frombuffer(r[0], dtype=">f4").astype(np.float64)
        return out
    finally:
        con.close()


def _cos(a, b, d):
    a, b = np.asarray(a, dtype=np.float64)[:d], np.asarray(b, dtype=np.float64)[:d]
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _check_vecs(e, vs, n):
    if len(vs) != n:
        refuse("%s returned %d vectors for %d texts" % (ITS.MODEL[e], len(vs), n))
    for v in vs:
        a = np.asarray(v, dtype=np.float64)
        if a.shape != (native(e),):
            refuse("%s returned a %d-d vector (native %d)" % (ITS.MODEL[e], a.size, native(e)))
        if not np.all(np.isfinite(a)) or not np.linalg.norm(a) > 0:
            refuse("%s returned a non-finite or zero vector" % ITS.MODEL[e])


def raw_digest(e, emb_dir):
    return ITS.read_meta(ITS.emb_path(e, emb_dir)).get("model_digest")


def preflight(e, texts, emb_dir, embed_fn, digest_fn, stored=()):
    """T1-T4 (docstring). stored = the card file's texts (the caller's state read). -> (digest, {d: [cos(CARD, RAW)]})."""
    model, pre, bar = ITS.MODEL[e], PROMPTS[e], ITS.PARITY_BAR[e]
    print("%s Ollama endpoint %s (resolved from OLLAMA_HOST=%r by embedder_arms.client_base)" % (TAG, EA.OLLAMA_URL, os.environ.get("OLLAMA_HOST")))
    dg, dr = digest_fn(model), raw_digest(e, emb_dir)
    print("%s T1 /api/tags: %s digest %s; S0's RAW file intent_emb_%s.db stored digest %s" % (TAG, model, dg, e, dr))
    if not dg:
        refuse("T1: %s is not listed by /api/tags: nothing is posted" % model)
    if dg != dr:
        refuse("T1: %s digest %s != S0's RAW file's digest %s: the CARD arm must be the RAW arm's weights (CW3)" % (model, dg, dr))
    chosen = texts[:PARITY_N]
    raw = _read_blobs(ITS.emb_path(e, emb_dir), chosen)
    vr = embed_fn(model, list(chosen))
    _check_vecs(e, vr, len(chosen))
    par = [_cos(raw[t], v, EA.PARITY_SLICE) for t, v in zip(chosen, vr)]
    print("%s T2 RAW route parity %s: %d texts posted without a prefix vs S0's stored RAW vectors, cos after slice-%d + renormalise "
          "min %.6f median %.6f (S0's bar >= %.4f): %s" % (TAG, model, len(par), EA.PARITY_SLICE, min(par), float(np.median(par)), bar,
                                                           "PASS" if min(par) >= bar else "FAIL"))
    if not min(par) >= bar:
        refuse("T2: RAW route parity min cos %.6f < %.4f" % (min(par), bar))
    v1 = embed_fn(model, [pre + t for t in chosen])
    _check_vecs(e, v1, len(chosen))
    cos = {d: [_cos(a, raw[t], d) for t, a in zip(chosen, v1)] for d in COS_SLICES[e]}
    for d in COS_SLICES[e]:
        print("%s T2b cos(CARD, RAW) %s on %d texts (S0 text set, first %d by sha256), slice %d + renormalise: min %.6f median %.6f "
              "(the prompt is the treatment: PRINTED, NO BAR)" % (TAG, e, len(chosen), PARITY_N, d, min(cos[d]), float(np.median(cos[d]))))
    v2 = embed_fn(model, [pre + t for t in chosen])
    _check_vecs(e, v2, len(chosen))
    rep = [_cos(a, b, EA.PARITY_SLICE) for a, b in zip(v1, v2)]
    print("%s T3 repeatability %s CARD: %d inputs posted twice, cos after slice-%d + renormalise min %.6f median %.6f (bar >= %.4f): %s"
          % (TAG, e, len(rep), EA.PARITY_SLICE, min(rep), float(np.median(rep)), bar, "PASS" if min(rep) >= bar else "FAIL"))
    if not min(rep) >= bar:
        refuse("T3: repeatability min cos %.6f < %.4f" % (min(rep), bar))
    p = card_path(e, emb_dir)
    have = sorted(stored, key=sha_text)[:PARITY_N]
    if have:
        st = _read_blobs(p, have)
        new = embed_fn(model, [pre + t for t in have])
        _check_vecs(e, new, len(have))
        rp = [_cos(st[t], v, EA.PARITY_SLICE) for t, v in zip(have, new)]
        print("%s T4 resume parity %s: %d stored rows re-embedded with the prefix, cos after slice-%d + renormalise min %.6f median %.6f "
              "(bar >= %.4f): %s" % (TAG, os.path.basename(p), len(rp), EA.PARITY_SLICE, min(rp), float(np.median(rp)), bar,
                                     "PASS" if min(rp) >= bar else "FAIL"))
        if not min(rp) >= bar:
            refuse("T4: resume parity min cos %.6f < %.4f" % (min(rp), bar))
    else:
        print("%s T4 resume parity: 0 stored rows in %s: first launch, nothing to compare" % (TAG, os.path.basename(p)))
    return dg, cos


def timed_probe(e, texts, embed_fn, n_todo, n=PROBE_N):
    sub = texts[:n]
    t0 = time.perf_counter()
    for s in range(0, len(sub), EA.BATCH):
        embed_fn(ITS.MODEL[e], [PROMPTS[e] + t for t in sub[s:s + EA.BATCH]])
    dt = max(time.perf_counter() - t0, 1e-9)
    rate = len(sub) / dt
    print("%s PRICE %s CARD: timed probe %d texts (with the prefix) in %.1f s = %.1f texts/s -> %d texts to embed = %.1f min (estimate "
          "from the probe)" % (TAG, e, len(sub), dt, rate, n_todo, n_todo / rate / 60.0))
    return rate


def _state(path, want):
    if os.path.exists(path):
        ITS.check_meta(path, want)
        return True, ITS.present_texts(path)
    return False, set()


def _check_e(e):
    if e not in EMB:
        refuse("--embedder %r is not one of %s" % (e, EMB))


def dry_run(e, db=None, emb_dir=None, embed_fn=None, digest_fn=None, probe_n=PROBE_N, prompts_file=None, prompts_sha=None):
    _check_e(e)
    db, emb_dir = db or II.DEFAULT_OUT, emb_dir or ITS.DATA_ROOT
    embed_fn, digest_fn = embed_fn or EA.ollama_embed, digest_fn or EA.model_digest
    print("%s pool of record: none (S0's intent corpora); zero judge calls; DRY RUN: nothing written; the preflight and the probe POST "
          "embeddings (Ollama), nothing else" % TAG)
    ITS.check_emb_dir(emb_dir)
    path = card_path(e, emb_dir)
    target_check(path)
    psha = load_prompts(prompts_file, prompts_sha)
    sha, texts, set_sha = load_inputs(e, db, emb_dir)
    want = expected_meta_card(e, set_sha, len(texts), sha["ingest_db"], psha)
    exists, have = _state(path, want)
    todo = sum(1 for t in texts if t not in have)
    print("%s DB paths: CARD %s (%s); RAW (read only) %s" % (TAG, path, "exists (RESUME)" if exists else "absent (new)", ITS.emb_path(e, emb_dir)))
    print("%s text set %d texts sha256 %s; %s: %d present, %d to embed" % (TAG, len(texts), set_sha, os.path.basename(path), len(have), todo))
    heavy_check()
    disk_line(emb_dir, "dry-run")
    preflight(e, texts, emb_dir, embed_fn, digest_fn, stored=have)
    timed_probe(e, texts, embed_fn, todo, n=probe_n)
    print("%s TRANSPORT PREFLIGHT PASSED (T0-T4) for %s" % (TAG, e))
    after_check(sha, db, emb_dir)
    print("%s dry: nothing written" % TAG)
    return 0


def embed(e, go, limit=None, db=None, emb_dir=None, embed_fn=None, digest_fn=None, prompts_file=None, prompts_sha=None):
    _check_e(e)
    db, emb_dir = db or II.DEFAULT_OUT, emb_dir or ITS.DATA_ROOT
    embed_fn, digest_fn = embed_fn or EA.ollama_embed, digest_fn or EA.model_digest
    ITS.check_emb_dir(emb_dir)
    path = card_path(e, emb_dir)
    target_check(path)
    psha = load_prompts(prompts_file, prompts_sha)
    sha, texts, set_sha = load_inputs(e, db, emb_dir)
    want = expected_meta_card(e, set_sha, len(texts), sha["ingest_db"], psha)
    exists, have = _state(path, want)
    miss = [t for t in texts if t not in have]
    todo = miss if limit is None else [t for t in texts[:int(limit)] if t not in have]
    print("%s embed %s (%s, CARD prompt sha256 %s) -> %s (%s): text set %d (sha256 %s), present %d, missing %d, this launch %d%s"
          % (TAG, e, ITS.MODEL[e], sha_text(PROMPTS[e])[:16], path, "exists: RESUME" if exists else "new", len(texts), set_sha[:16],
             len(have), len(miss), len(todo), "" if limit is None else " (--limit %d)" % int(limit)))
    if not go:
        print("%s dry: nothing posted, nothing written (add --go)" % TAG)
        return 0
    heavy_check()
    disk_line(emb_dir, "before")
    before = ITS.record_table_hashes()
    print("%s shared caches per-table before: %s" % (TAG, json.dumps(before, sort_keys=True)))
    digest, _cos_ = preflight(e, texts, emb_dir, embed_fn, digest_fn, stored=have)
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
    n = EA.write_vectors(path, card_arm(e), todo, embed_fn) if todo else 0
    after = ITS.record_table_hashes()
    if after != before:
        refuse("the shared caches' per-table hashes CHANGED during the embedding: before %s after %s" % (before, after))
    print("%s shared caches per-table after: unchanged" % TAG)
    after_check(sha, db, emb_dir)
    disk_line(emb_dir, "after")
    left = len(miss) - n
    print("%s embed %s CARD: wrote %d; %d of the set still missing%s" % (TAG, e, n, left, "" if left else " (COMPLETE)"))
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
    """In-process embed_fn / digest_fn over the fixture's RAW vectors. An input WITHOUT a prefix returns the stored RAW vector (+
    `raw_drift` noise); an input WITH e's prefix returns RAW + a deterministic perturbation of scale `eps` (so cos(CARD, RAW) is known),
    optionally a per-call jitter, a wrong dimension or a zero vector. `hook(n, model, inputs)` runs at every call (planted tampering)."""

    def __init__(self, raw, eps=0.05, jitter=0.0, dim=None, zero=False, digests=None, raw_drift=0.0, hook=None):
        self.raw, self.eps, self.jitter, self.dim, self.zero, self.raw_drift, self.hook = raw, eps, jitter, dim, zero, raw_drift, hook
        self.calls, self.n = [], 0
        self.digests = digests

    def e_of(self, model):
        return [e for e in EMB if ITS.MODEL[e] == model][0]

    def card_vec(self, e, t, call):
        base = self.raw[e][t]
        nat = len(base)
        r = np.random.default_rng(int(hashlib.sha256(("card" + e + t).encode("utf-8")).hexdigest()[:8], 16))
        v = base + self.eps * np.linalg.norm(base) / np.sqrt(nat) * r.normal(size=nat)
        if self.jitter:
            rj = np.random.default_rng(call * 7919 + int(hashlib.sha256(t.encode("utf-8")).hexdigest()[:6], 16))
            v = v + self.jitter * np.linalg.norm(base) / np.sqrt(nat) * rj.normal(size=nat)
        return v

    def vec(self, e, inp, call):
        pre = PROMPTS[e]
        if inp.startswith(pre):
            v = self.card_vec(e, inp[len(pre):], call)
        else:
            v = np.array(self.raw[e][inp], dtype=np.float64)
            if self.raw_drift:
                r = np.random.default_rng(int(hashlib.sha256(("drift" + inp).encode("utf-8")).hexdigest()[:8], 16))
                v = v + self.raw_drift * np.linalg.norm(v) / np.sqrt(len(v)) * r.normal(size=len(v))
        if self.zero:
            v = np.zeros(len(v))
        dim = self.dim or len(v)
        return [float(x) for x in v[:dim]] + [0.0] * max(0, dim - len(v))

    def embed(self, model, inputs):
        self.n += 1
        self.calls.append((model, list(inputs)))
        if self.hook:
            self.hook(self.n, model, inputs)
        e = self.e_of(model)
        return [self.vec(e, x, self.n) for x in inputs]

    def digest(self, model, url=None):
        return "stub" if self.digests is None else self.digests.get(model)


def build_fixture(td):
    """S0's own fixture (ingest DB + intent_emb_{qwen3,nomic,gemma}.db, planted, meta digest "stub"), its pins file, a planted shared
    cache (embeddings_cache.db) under the fixture DATA_ROOT, and a prompts file equal to the committed one."""
    with contextlib.redirect_stdout(io.StringIO()):
        db, CS, texts, derived = ITS.build_fixture(td)
    pins = ITS._pins_file(td, db, td)
    raw = {}
    for e in EMB:
        con = sqlite3.connect(ITS.emb_path(e, td))
        raw[e] = {t: np.frombuffer(b, dtype=">f4").astype(np.float64) for t, b in con.execute("SELECT query, vector FROM embeddings")}
        con.close()
    return {"td": td, "db": db, "pins": pins, "texts": texts, "raw": raw}


def _plant_shared(d):
    p = os.path.join(d, "embeddings_cache.db")
    con = sqlite3.connect(p)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("INSERT INTO embeddings VALUES ('a', x'00')")
    con.commit()
    con.close()
    return p


@contextlib.contextmanager
def _scope(fx):
    """Fixture scope: S0's fixture K, the fixture's pins, no heavy process, S0's DATA_ROOT = the fixture directory (the shared-cache
    hashes read the planted cache only), Ollama on a closed port (nothing real is contacted); restored on exit."""
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
    for f in (II.DB_NAME,) + tuple("intent_emb_%s.db" % e for e in EMB):
        shutil.copyfile(os.path.join(fx["td"], f), os.path.join(d, f))
    _plant_shared(d)
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
            td = tempfile.mkdtemp(prefix="cpw_st_")
            with _scope({"pins": None}):
                fixture = build_fixture(td)
        _selftest(sel, ok, fixture)
    finally:
        if td:
            shutil.rmtree(td, ignore_errors=True)
    if not quiet:
        print("SELFTEST (writer): %d checks passed" % n[0])
    return 0


def _go(fx, name, e, st, pre=None, **kw):
    f = _fresh(fx, name)
    if pre:
        pre(f)
    with _scope(f):
        o, err, r = _cap(lambda: embed(e, True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, **kw))
    return o, err, r, f


def _selftest(sel, ok, fx):
    if sel("W-CONST"):
        ok(check_its_blob() == ITS_BLOB, "W-CONST intent_transfer_s0.py is blob f662ceb (imported unchanged)")
        ok(PROMPTS["qwen3"] == "Instruct: Given a user utterance to a virtual assistant, identify the user's intent" + chr(10) + "Query:",
           "W-CONST qwen3 prompt = the registered card query form, one LF byte, no space after 'Query:'")
        ok(PROMPTS["gemma"] == "task: clustering | query: " and PROMPTS["nomic"] == "clustering: ", "W-CONST gemma / nomic prompts as registered")
        ok(sha_text(PROMPTS["qwen3"]).startswith("e92a9484") and sha_text(PROMPTS["gemma"]).startswith("11ab9b67")
           and sha_text(PROMPTS["nomic"]).startswith("1885ff31"), "W-CONST prompt sha256 e92a9484 / 11ab9b67 / 1885ff31")
        ok({e: ITS.MODEL[e] for e in EMB} == {"qwen3": "qwen3-embedding:latest", "gemma": "embeddinggemma:latest", "nomic": "nomic-embed-text:latest"},
           "W-CONST models = S0's RAW arms' models (qwen3 = the Q4_K_M tag)")
        ok({e: native(e) for e in EMB} == {"qwen3": 4096, "gemma": 768, "nomic": 768}, "W-CONST native dims 4096 / 768 / 768")
        ok(all(card_arm(e).prefix == PROMPTS[e] and card_arm(e).layer_norm is False for e in EMB), "W-CONST card arms: prefix, no transform (CW1)")
        ok([os.path.basename(card_path(e, "x")) for e in EMB] == ["intent_emb_qwen3_card.db", "intent_emb_gemma_card.db", "intent_emb_nomic_card.db"],
           "W-CONST files intent_emb_{qwen3,gemma,nomic}_card.db")
        ok({e: ITS.PARITY_BAR[e] for e in EMB} == {"qwen3": 0.998, "gemma": 0.9999, "nomic": 0.9999} and PARITY_N == 20,
           "W-CONST S0's bars 0.998 / 0.9999 / 0.9999 on 20 texts")
        o, err, sha = _cap(lambda: load_prompts())
        ok(err is None and sha == PROMPTS_FILE_SHA, "W-CONST the committed prompts file reads PIN OK (sha256 %s)" % PROMPTS_FILE_SHA[:16])
        ok(("%r sha256 %s" % (PROMPTS["qwen3"], sha_text(PROMPTS["qwen3"]))) in _line(o, "T0 prompt qwen3"), "W-CONST T0 prints the qwen3 string and its sha256")
    if sel("W-T0"):
        td = os.path.join(fx["td"], "t0_%d" % len(os.listdir(fx["td"])))
        os.makedirs(td)
        good = open(PROMPTS_FILE, "rb").read()
        p = os.path.join(td, "p.json")
        open(p, "wb").write(good.replace(b"\r\n", b"\n").replace(b"\\nQuery:\"", b"\\nQuery: \""))
        o, err, _r = _cap(lambda: load_prompts(p))
        ok(err and "T0" in err and "sha256" in err, "W-T0 a prompts file with a space after 'Query:' fails the file pin")
        js = json.loads(good.decode("utf-8"))
        js["gemma"] = "task: clustering | query:"
        b = json.dumps(js).encode("utf-8")
        open(p, "wb").write(b)
        o, err, _r = _cap(lambda: load_prompts(p, hashlib.sha256(b).hexdigest()))
        ok(err and "gemma prompt" in err, "W-T0 a re-pinned file whose gemma string differs from the constant REFUSES (double entry)")
        open(p, "wb").write(good.replace(b"\n", b"\r\n") if b"\r\n" not in good else good)
        o, err, sha = _cap(lambda: load_prompts(p))
        ok(err is None and sha == PROMPTS_FILE_SHA and "CRLF working-tree sha256" in o, "W-T0 a CRLF checkout of the file hashes to the LF pin (CRLF sha printed beside)")
        saved_q = PROMPTS["qwen3"]
        try:
            for bad_q in ("Instruct: x" + chr(10) + "Query: ", "Instruct: x" + chr(13) + chr(10) + "Query:", "Instruct: x Query:",
                          "Instruct: x" + chr(10) + "y" + chr(10) + "Query:"):
                PROMPTS["qwen3"] = bad_q
                js2 = dict(js, gemma=PROMPTS["gemma"], qwen3=bad_q)
                b = json.dumps(js2).encode("utf-8")
                open(p, "wb").write(b)
                o, err, _r = _cap(lambda: load_prompts(p, hashlib.sha256(b).hexdigest()))
                ok(err and "card form" in err, "W-T0 a qwen3 string %r off the card form REFUSES even when file and constant agree" % bad_q)
        finally:
            PROMPTS["qwen3"] = saved_q
    if sel("W-GO"):
        for e in ("qwen3", "gemma"):
            st = Stub(fx["raw"], eps=0.3)
            o, err, res, f = _go(fx, "go_" + e, e, st)
            ok(err is None, "W-GO %s --embed --go completes on the fixture (%s)" % (e, err))
            path = card_path(e, f["emb_dir"])
            rows, meta = _rows(path)
            ok(set(rows) == set(fx["texts"]) and res == len(fx["texts"]), "W-GO %s every text of S0's set written under the RAW text (%d)" % (e, len(rows)))
            t0 = fx["texts"][5]
            ok(np.allclose(rows[t0], np.asarray(st.card_vec(e, t0, 0), dtype=">f4").astype(np.float64)), "W-GO %s stored vector = the CARD vector (prefix posted)" % e)
            ok(all(len(v) == native(e) for v in rows.values()), "W-GO %s every stored vector %d-d" % (e, native(e)))
            psha = hashlib.sha256(open(PROMPTS_FILE, "rb").read().replace(b"\r\n", b"\n")).hexdigest()
            ok(meta["protocol"] == "CARD" and meta["embedder"] == e + "_card" and meta["model"] == ITS.MODEL[e] and meta.get("prompt") == PROMPTS[e]
               and meta["prompt_sha256"] == sha_text(PROMPTS[e]) and meta["prompts_file_sha256"] == psha and meta["model_digest"] == "stub"
               and meta["writer_blob_lf"] == writer_blob() and meta["script_blob_lf"] == ITS_BLOB,
               "W-GO %s intent_meta: protocol CARD, embedder, model, prompt + sha256, prompts file sha, digest, writer and S0 blobs" % e)
            set_sha = ITS.text_set(ITS.load_corpora(f["db"]))[1]
            ok(meta["text_set_sha256"] == set_sha and meta["n_texts"] == str(len(fx["texts"])), "W-GO %s intent_meta pins S0's text set and count" % e)
            ok("(COMPLETE)" in _line(o, "embed %s CARD: wrote" % e), "W-GO %s prints COMPLETE" % e)
            wr = [c for c in st.calls[3:]]
            ok(wr and all(all(x.startswith(PROMPTS[e]) for x in inp) for _m, inp in wr)
               and sorted(x[len(PROMPTS[e]):] for _m, inp in wr for x in inp) == sorted(fx["texts"]),
               "W-GO %s every write POST carries the prefix, every text exactly once (%d posts)" % (e, len(wr)))
            ok(st.calls[0][1] == fx["texts"][:20] and st.calls[1][1] == [PROMPTS[e] + t for t in fx["texts"][:20]]
               and st.calls[2][1] == st.calls[1][1], "W-GO %s preflight: T2 posts the first 20 RAW, T2b and T3 the same 20 with the prefix" % e)
            ok("min 1.000000" in _line(o, "T2 RAW route parity") and "PASS" in _line(o, "T2 RAW route parity"), "W-GO %s T2 RAW parity PASS at 1.000000" % e)
            for d in COS_SLICES[e]:
                exp = sorted(_cos(st.card_vec(e, t, 0), fx["raw"][e][t], d) for t in fx["texts"][:20])
                ln = _line(o, "T2b cos(CARD, RAW) %s on 20 texts (S0 text set, first 20 by sha256), slice %d " % (e, d))
                ok(("min %.6f median %.6f" % (exp[0], float(np.median(exp)))) in ln and "NO BAR" in ln and exp[0] < 0.999,
                   "W-GO %s T2b cos(CARD, RAW) slice %d min / median = an independent recomputation (%.6f / %.6f)" % (e, d, exp[0], float(np.median(exp))))
            ok("first launch" in _line(o, "T4"), "W-GO %s T4 first launch: nothing to compare" % e)
        st = Stub(fx["raw"], eps=0.3)
        o, err, res, f = _go(fx, "go_nomic", "nomic", st, limit=30)
        rows, meta = _rows(card_path("nomic", f["emb_dir"]))
        ok(err is None and len(rows) == 30 and meta["prompt"] == "clustering: " and all(len(v) == 768 for v in rows.values()),
           "W-GO nomic (descriptive arm): --limit 30 writes 30 rows, prompt 'clustering: ', 768-d")
        # resume: a partial file continues; T4 compares stored rows (a 7-row file is compared too: all 7)
        f2 = _fresh(fx, "resume")
        st2 = Stub(fx["raw"], eps=0.3)
        with _scope(f2):
            _cap(lambda: embed("gemma", True, limit=7, db=f2["db"], emb_dir=f2["emb_dir"], embed_fn=st2.embed, digest_fn=st2.digest))
            n7 = len(_rows(card_path("gemma", f2["emb_dir"]))[0])
            o2, err2, res2 = _cap(lambda: embed("gemma", True, db=f2["db"], emb_dir=f2["emb_dir"], embed_fn=st2.embed, digest_fn=st2.digest))
        ok(n7 == 7 and err2 is None and res2 == len(fx["texts"]) - 7, "W-GO --limit 7 then resume: 7 then the remaining %d" % (len(fx["texts"]) - 7))
        t4 = _line(o2, "T4 resume parity")
        ok("7 stored rows" in t4 and "PASS" in t4 and "min 1.000000" in t4, "W-GO T4 on a 7-row file compares all 7 rows, PASS at 1.000000 (READY_embed_quant D3)")
        gb = shutil.disk_usage(f2["emb_dir"]).free / 1e9
        dl = [float(_line(o2, "DISK %s" % w).split(": ")[1].split(" GB")[0]) for w in ("before", "after")]
        ok(all(abs(x - gb) < 1.0 for x in dl), "W-GO DISK before / after printed in GB (%.2f / %.2f)" % (dl[0], dl[1]))
    if sel("W-REFUSE"):
        e = "gemma"
        o, err, _r, f = _go(fx, "unlisted", e, Stub(fx["raw"], digests={}))
        ok(err and "T1" in err and "not listed" in err and not os.path.exists(card_path(e, f["emb_dir"])), "W-REFUSE T1 tag not listed: refused, no file")
        st = Stub(fx["raw"], digests={ITS.MODEL[e]: "sha256:REPULLED"})
        o, err, _r, f = _go(fx, "otherdigest", e, st)
        ok(err and "T1" in err and "RAW file's digest" in err and st.n == 0, "W-REFUSE T1 a digest other than S0's RAW file's: refused, nothing posted")
        st = Stub(fx["raw"], raw_drift=0.05)
        o, err, _r, f = _go(fx, "rawdrift", e, st)
        ok(err and "T2" in err and "RAW route parity" in err and not os.path.exists(card_path(e, f["emb_dir"])),
           "W-REFUSE T2 the RAW route no longer reproduces S0's vectors (bar 0.9999): refused, no file")
        st = Stub(fx["raw"], raw_drift=0.15)
        o, err, _r, f = _go(fx, "rawdrift_q", "qwen3", st, limit=25)
        ln = _line(o, "T2 RAW route parity")
        ok(err is None and "PASS" in ln and "bar >= 0.9980" in ln and float(ln.split("min ")[1].split()[0]) < 0.9999,
           "W-REFUSE T2 qwen3's own bar 0.998 admits a drift below gemma's 0.9999 (per-embedder bar executed)")
        o, err, _r, f = _go(fx, "wrongdim", e, Stub(fx["raw"], dim=1024))
        ok(err and "1024-d" in err and not os.path.exists(card_path(e, f["emb_dir"])), "W-REFUSE a 1024-d vector for gemma: refused, no file")
        o, err, _r, f = _go(fx, "zero", e, Stub(fx["raw"], zero=True))
        ok(err and "zero vector" in err, "W-REFUSE a zero vector: refused")
        o, err, _r, f = _go(fx, "jitter", e, Stub(fx["raw"], jitter=0.05))
        ok(err and "T3" in err and not os.path.exists(card_path(e, f["emb_dir"])), "W-REFUSE T3 repeatability below 0.9999: refused, no file")
        o, err, _r, f = _go(fx, "jitter_q", "qwen3", Stub(fx["raw"], jitter=0.02), limit=25)
        ok(err is None and "PASS" in _line(o, "T3"), "W-REFUSE T3 qwen3 at a jitter inside 0.998 passes (both branches executed)")

        def tamper(f):
            st = Stub(fx["raw"])
            with _scope(f):
                _cap(lambda: embed(e, True, limit=40, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
            con = sqlite3.connect(card_path(e, f["emb_dir"]))
            for t, in con.execute("SELECT query FROM embeddings").fetchall():
                con.execute("UPDATE embeddings SET vector = ? WHERE query = ?", (np.asarray(-fx["raw"][e][t], dtype=">f4").tobytes(), t))
            con.commit()
            con.close()
        o, err, _r, f = _go(fx, "t4", e, Stub(fx["raw"]), pre=tamper)
        ok(err and "T4" in err, "W-REFUSE T4 stored rows that the CARD route no longer reproduces: refused")

        def remeta(key, val):
            def pre(f):
                st = Stub(fx["raw"])
                with _scope(f):
                    _cap(lambda: embed(e, True, limit=40, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
                con = sqlite3.connect(card_path(e, f["emb_dir"]))
                con.execute("UPDATE intent_meta SET value = ? WHERE key = ?", (val, key))
                con.commit()
                con.close()
            return pre
        for key, val in (("writer_blob_lf", "x"), ("prompt", "task: clustering | query:"), ("prompt_sha256", "0" * 64), ("protocol", "RAW")):
            st = Stub(fx["raw"])
            o, err, _r, f = _go(fx, "remeta_" + key, e, st, pre=remeta(key, val))
            ok(err and key in err and "intent_meta mismatch" in err and st.n == 0, "W-REFUSE a file started under another %s is never resumed (0 posts)" % key)
        st = Stub(fx["raw"])
        o, err, _r, f = _go(fx, "remeta_digest", e, st, pre=remeta("model_digest", "sha256:OTHER"))
        ok(err and "intent_meta mismatch on ['model_digest']" in err and not _line(o, "embed gemma CARD: wrote"),
           "W-REFUSE a file whose stored digest differs from the tag's is never resumed (nothing written)")
        f = _fresh(fx, "race")
        st = Stub(fx["raw"])
        racer = {"p": card_path(e, f["emb_dir"])}

        def racing_digest(model, url=None):          # the file appears between the state read and the exclusive create
            if not os.path.exists(racer["p"]):
                open(racer["p"], "wb").close()
            return st.digest(model)
        raced = None
        with _scope(f):
            try:
                _cap(lambda: embed(e, True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=racing_digest))
            except FileExistsError as ex:
                raced = ex
        ok(raced is not None and os.path.getsize(racer["p"]) == 0, "W-REFUSE a file that appears before the first write is never written (exclusive create)")
        f = _fresh(fx, "heavy")
        st = Stub(fx["raw"])
        with _scope(f):
            ITS._foreign_heavy = lambda: ['"java.exe","123"']
            o, err, _r = _cap(lambda: embed(e, True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "heavy" in err and st.n == 0, "W-REFUSE a java.exe running: refused before any POST")
        f = _fresh(fx, "pinbad")
        bad = os.path.join(f["emb_dir"], "pins_bad.json")
        p = json.load(open(fx["pins"]))
        p["emb"][e] = "0" * 64
        json.dump(p, open(bad, "w"))
        st = Stub(fx["raw"])
        with _scope(f):
            ITS.PINS_FILE_OVERRIDE[0] = bad
            o, err, _r = _cap(lambda: embed(e, True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "intent_emb_gemma.db" in err and st.n == 0, "W-REFUSE S0's RAW gemma file off its pin: refused before any POST")
        p["emb"][e] = None
        json.dump(p, open(bad, "w"))
        with _scope(f):
            ITS.PINS_FILE_OVERRIDE[0] = bad
            o, err, _r = _cap(lambda: embed(e, True, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err and "UNPINNED" in err, "W-REFUSE an unpinned RAW file: refused (S0's pins strict)")
        f = _fresh(fx, "nogo")
        st = Stub(fx["raw"])
        with _scope(f):
            o, err, r = _cap(lambda: embed(e, False, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err is None and r == 0 and st.n == 0 and not os.path.exists(card_path(e, f["emb_dir"])), "W-REFUSE without --go: nothing posted, nothing written")
        o, err, _r = _cap(lambda: embed("mxbai", True))
        ok(err and "not one of" in err, "W-REFUSE an embedder outside qwen3 / gemma / nomic")
    if sel("W-WAL"):
        e = "gemma"
        for sfx in ("-wal", "-journal"):
            def plant(f, sfx=sfx):
                open(card_path(e, f["emb_dir"]) + sfx, "wb").write(b"\x01")
            st = Stub(fx["raw"])
            o, err, _r, f = _go(fx, "wal_absent" + sfx, e, st, pre=plant)
            ok(err and ("intent_emb_gemma_card.db" + sfx) in err and "non-empty" in err and st.n == 0 and not os.path.exists(card_path(e, f["emb_dir"])),
               "W-WAL a 1-byte %s beside an ABSENT target: --embed --go refused, 0 posts, no file (READY_embed_quant OM5)" % sfx)
            f = _fresh(fx, "dry_wal" + sfx)
            plant(f)
            st = Stub(fx["raw"])
            with _scope(f):
                o, err, _r = _cap(lambda: dry_run(e, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, probe_n=40))
            ok(err and "non-empty" in err and st.n == 0, "W-WAL the same %s refuses the --dry-run too, 0 posts" % sfx)

        def partial_then_wal(f):
            st = Stub(fx["raw"])
            with _scope(f):
                _cap(lambda: embed(e, True, limit=40, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
            open(card_path(e, f["emb_dir"]) + "-wal", "wb").write(b"\x01" * 100)
        st = Stub(fx["raw"])
        o, err, _r, f = _go(fx, "wal_partial", e, st, pre=partial_then_wal)
        ok(err and "non-empty" in err and st.n == 0, "W-WAL a 100-byte -wal beside a 40-row partial file: refused, 0 posts")
        f = _fresh(fx, "wal_empty")
        open(card_path(e, f["emb_dir"]) + "-wal", "wb").close()
        st = Stub(fx["raw"])
        with _scope(f):
            o, err, r = _cap(lambda: embed(e, True, limit=25, db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest))
        ok(err is None and r == 25, "W-WAL a 0-byte -wal is admitted (only a NON-EMPTY sidecar refuses; both branches executed)")
    if sel("W-HASH"):
        e = "gemma"

        def shared_hook(fx_):
            def hook(n, model, inputs):
                if n == 4:                                 # the first write batch (after T2, T2b, T3)
                    con = sqlite3.connect(os.path.join(ITS.DATA_ROOT, "embeddings_cache.db"))
                    con.execute("INSERT INTO embeddings VALUES ('b', x'01')")
                    con.commit()
                    con.close()
            return hook
        st = Stub(fx["raw"], hook=shared_hook(fx))
        o, err, _r, f = _go(fx, "shared", e, st)
        ok(err and "shared caches' per-table hashes CHANGED" in err, "W-HASH a shared cache changed during the pass (planted in embed_fn): REFUSED (OM6)")
        ok("embeddings_cache.db" in _line(o, "shared caches per-table before") and "absent" not in _line(o, "shared caches per-table before").split("embeddings_cache.db")[1][:12],
           "W-HASH the planted shared cache is hashed (not 'absent') before the pass")

        def raw_hook(n, model, inputs):
            if n == 4:
                with open(ITS.emb_path(e, ITS.DATA_ROOT), "ab") as fh:
                    fh.write(b"\0")
        st = Stub(fx["raw"], hook=raw_hook)
        o, err, _r, f = _go(fx, "s0after", e, st)
        ok(err and "gemma sha256 changed during the embedding" in err, "W-HASH a byte appended to S0's RAW file during the pass: REFUSED by the after-check (OM7)")

        def ingest_hook(n, model, inputs):
            if n == 4:
                with open(os.path.join(ITS.DATA_ROOT, II.DB_NAME), "ab") as fh:
                    fh.write(b"\0")
        st = Stub(fx["raw"], hook=ingest_hook)
        o, err, _r, f = _go(fx, "ingestafter", e, st)
        ok(err and "ingest_db sha256 changed" in err, "W-HASH a byte appended to S0's ingest DB during the pass: REFUSED")
        st = Stub(fx["raw"])
        o, err, _r, f = _go(fx, "clean", e, st, limit=40)
        ok(err is None and "shared caches per-table after: unchanged" in o and "S0's pins re-checked after: unchanged" in o,
           "W-HASH an untouched pass prints both after-checks unchanged (both branches executed)")
    if sel("W-DRY"):
        f = _fresh(fx, "dry")
        st = Stub(fx["raw"], eps=0.3)
        with _scope(f):
            o, err, r = _cap(lambda: dry_run("qwen3", db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, probe_n=64))
        ok(err is None and "TRANSPORT PREFLIGHT PASSED (T0-T4) for qwen3" in o and not os.path.exists(card_path("qwen3", f["emb_dir"])),
           "W-DRY qwen3 preflight passes, nothing written")
        ok(all(("T0 prompt %s" % e2) in o for e2 in EMB) and "PIN OK" in _line(o, "T0 prompts file"), "W-DRY prints the three strings and the prompts-file pin")
        ok(("%d to embed" % len(fx["texts"])) in _line(o, "text set") and "PRICE qwen3 CARD" in o
           and st.calls[-1][1] == [PROMPTS["qwen3"] + t for t in fx["texts"][32:64]], "W-DRY counts %d to embed; the probe posts 64 texts WITH the prefix" % len(fx["texts"]))
        ok("intent_emb_qwen3_card.db" in _line(o, "DB paths") and "intent_emb_qwen3.db" in _line(o, "DB paths"), "W-DRY prints the CARD and RAW DB paths")
        st = Stub(fx["raw"], digests={})
        with _scope(f):
            o, err, r = _cap(lambda: dry_run("qwen3", db=f["db"], emb_dir=f["emb_dir"], embed_fn=st.embed, digest_fn=st.digest, probe_n=64))
        ok(err and "not listed" in err and "PASSED" not in o, "W-DRY an unlisted tag fails the dry-run's preflight")
    if sel("W-HTTP"):
        # the real ollama_embed / model_digest path against embedder_arms' stub Ollama (127.0.0.1, ephemeral port; nothing real)
        f = _fresh(fx, "http")
        e = "gemma"
        with _scope(f):
            with EA.stub_ollama() as (url, log, state):
                EA.OLLAMA_URL = url
                con = sqlite3.connect(ITS.emb_path(e, f["emb_dir"]))
                con.execute("UPDATE intent_meta SET value = ? WHERE key = 'model_digest'", ("stubdigest-" + ITS.MODEL[e],))
                rows = con.execute("SELECT query FROM embeddings").fetchall()
                for (t,) in rows:
                    con.execute("UPDATE embeddings SET vector = ? WHERE query = ?",
                                (np.asarray(EA._stub_vec(t, native(e)), dtype=">f4").tobytes(), t))
                con.commit()
                con.close()
                pj = json.load(open(f["pins"]))
                pj["emb"][e] = II.file_sha(ITS.emb_path(e, f["emb_dir"]))
                pf = os.path.join(f["emb_dir"], "pins_http.json")
                json.dump(pj, open(pf, "w"))
                ITS.PINS_FILE_OVERRIDE[0] = pf
                o, err, r = _cap(lambda: embed(e, True, limit=40, db=f["db"], emb_dir=f["emb_dir"]))
        ok(err is None and r == 40, "W-HTTP through ollama_embed + /api/tags on the stub server: 40 rows (%s)" % err)
        rows, meta = _rows(card_path(e, f["emb_dir"]))
        ok(meta["model_digest"] == "stubdigest-" + ITS.MODEL[e], "W-HTTP the digest is stored from /api/tags")
        posted = [x for _p, m, inp in log if inp for x in (inp if isinstance(inp, list) else [inp])]
        ok(all(m == ITS.MODEL[e] for _p, m, _i in log) and sum(1 for x in posted if x.startswith(PROMPTS[e])) >= 40 + 40,
           "W-HTTP every request names the gemma tag; T2b/T3 and the 40 writes went out WITH the prefix (%d requests)" % len(log))


MUTANTS = (
    ("T2 posts with the prefix", "    vr = embed_fn(model, list(chosen))\n", "    vr = embed_fn(model, [pre + t for t in chosen])\n", ("W-GO",)),
    ("write_vectors with S0's RAW arm", "    n = EA.write_vectors(path, card_arm(e), todo, embed_fn)", "    n = EA.write_vectors(path, EA.ARMS[ITS.ARM[e]], todo, embed_fn)", ("W-GO",)),
    ("qwen3 prompt with a space after Query:", "identify the user's intent\\nQuery:\",\n", "identify the user's intent\\nQuery: \",\n", ("W-CONST",)),
    ("gemma prompt without the trailing space", "           \"gemma\": \"task: clustering | query: \",\n", "           \"gemma\": \"task: clustering | query:\",\n", ("W-CONST",)),
    ("prompts file pin not checked", "    if sha != want_sha:\n        refuse(\"T0:", "    if False:\n        refuse(\"T0:", ("W-T0",)),
    ("file value vs constant not checked", "        if js.get(e) != PROMPTS[e]:\n", "        if False:\n", ("W-T0",)),
    ("prompts file hashed CRLF", "    data = raw.replace(b\"\\r\\n\", b\"\\n\")\n", "    data = raw\n", ("W-T0",)),
    ("T1 unlisted tag admitted", "    if not dg:\n        refuse(", "    if False:\n        refuse(", ("W-REFUSE", "W-DRY")),
    ("T1 digest vs RAW file not compared", "    if dg != dr:\n", "    if False:\n", ("W-REFUSE",)),
    ("T2 bar dropped", "    if not min(par) >= bar:\n", "    if False:\n", ("W-REFUSE",)),
    ("T2 bar = qwen3's 0.998 for every embedder", "    model, pre, bar = ITS.MODEL[e], PROMPTS[e], ITS.PARITY_BAR[e]\n",
     "    model, pre, bar = ITS.MODEL[e], PROMPTS[e], ITS.PARITY_BAR[\"qwen3\"]\n", ("W-REFUSE",)),
    ("T3 bar dropped", "    if not min(rep) >= bar:\n", "    if False:\n", ("W-REFUSE",)),
    ("T4 skipped on resume", "    if have:\n        st = _read_blobs(p, have)\n", "    if len(have) >= PARITY_N:\n        st = _read_blobs(p, have)\n", ("W-GO",)),
    ("T4 bar dropped", "        if not min(rp) >= bar:\n", "        if False:\n", ("W-REFUSE",)),
    ("T2b min printed as max", "              \"(the prompt is the treatment: PRINTED, NO BAR)\" % (TAG, e, len(chosen), PARITY_N, d, min(cos[d]),",
     "              \"(the prompt is the treatment: PRINTED, NO BAR)\" % (TAG, e, len(chosen), PARITY_N, d, max(cos[d]),", ("W-GO",)),
    ("T2b cos against the CARD vectors themselves", "    cos = {d: [_cos(a, raw[t], d) for t, a in zip(chosen, v1)] for d in COS_SLICES[e]}\n",
     "    cos = {d: [_cos(a, a, d) for t, a in zip(chosen, v1)] for d in COS_SLICES[e]}\n", ("W-GO",)),
    ("cos without renormalisation", "    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))\n", "    return float(np.dot(a, b))\n", ("W-GO",)),
    ("dimension check removed", "        if a.shape != (native(e),):\n", "        if False:\n", ("W-REFUSE",)),
    ("zero-vector check removed", "        if not np.all(np.isfinite(a)) or not np.linalg.norm(a) > 0:\n", "        if False:\n", ("W-REFUSE",)),
    ("first launch not exclusive", "        with open(path, \"xb\"):", "        with open(path, \"ab\"):", ("W-REFUSE",)),
    ("meta without the prompt", "    m.update({\"embedder\": e + \"_card\", \"protocol\": PROTOCOL, \"prompt\": PROMPTS[e], ",
     "    m.update({\"embedder\": e + \"_card\", \"protocol\": PROTOCOL, ", ("W-GO", "W-REFUSE")),
    ("meta protocol RAW", "PROTOCOL = \"CARD\"\n", "PROTOCOL = \"RAW\"\n", ("W-GO", "W-REFUSE")),
    ("meta digest not checked on resume", "        ITS.check_meta(path, want, digest=digest)\n", "        pass\n", ("W-REFUSE",)),
    ("S0 pins not strict", "    sha[e] = ITS.pin_check(rp, \"emb\", True,", "    sha[e] = ITS.pin_check(rp, \"emb\", False,", ("W-REFUSE",)),
    ("RAW pin not checked", "    sha[e] = ITS.pin_check(rp, \"emb\", True, sub=e, label=\"intent_emb_%s.db\" % e)\n", "    sha[e] = II.file_sha(rp)\n", ("W-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("W-REFUSE",)),
    ("target_check is a no-op", "    ITS.check_emb_target(path)\n", "    pass\n", ("W-WAL",)),
    ("target_check not called in embed()", "    path = card_path(e, emb_dir)\n    target_check(path)\n    psha = load_prompts(prompts_file, prompts_sha)\n    sha, texts, set_sha = load_inputs(e, db, emb_dir)\n    want = expected_meta_card(e, set_sha, len(texts), sha[\"ingest_db\"], psha)\n    exists, have = _state(path, want)\n    miss",
     "    path = card_path(e, emb_dir)\n    psha = load_prompts(prompts_file, prompts_sha)\n    sha, texts, set_sha = load_inputs(e, db, emb_dir)\n    want = expected_meta_card(e, set_sha, len(texts), sha[\"ingest_db\"], psha)\n    exists, have = _state(path, want)\n    miss", ("W-WAL",)),
    ("target_check not called in dry_run()", "    path = card_path(e, emb_dir)\n    target_check(path)\n    psha = load_prompts(prompts_file, prompts_sha)\n    sha, texts, set_sha = load_inputs(e, db, emb_dir)\n    want = expected_meta_card(e, set_sha, len(texts), sha[\"ingest_db\"], psha)\n    exists, have = _state(path, want)\n    todo",
     "    path = card_path(e, emb_dir)\n    psha = load_prompts(prompts_file, prompts_sha)\n    sha, texts, set_sha = load_inputs(e, db, emb_dir)\n    want = expected_meta_card(e, set_sha, len(texts), sha[\"ingest_db\"], psha)\n    exists, have = _state(path, want)\n    todo", ("W-WAL",)),
    ("shared-cache compare disabled", "    if after != before:\n        refuse(\"the shared caches'", "    if False:\n        refuse(\"the shared caches'", ("W-HASH",)),
    ("S0 after_check removed from embed()", "    print(\"%s shared caches per-table after: unchanged\" % TAG)\n    after_check(sha, db, emb_dir)\n",
     "    print(\"%s shared caches per-table after: unchanged\" % TAG)\n", ("W-HASH",)),
    ("after_check ignores the ingest DB", "        now = II.file_sha(db if k == \"ingest_db\" else ITS.emb_path(k, emb_dir))\n        if now != s:\n            refuse(\"%s sha256 changed during the embedding",
     "        now = II.file_sha(db if k == \"ingest_db\" else ITS.emb_path(k, emb_dir))\n        if now != s and k != \"ingest_db\":\n            refuse(\"%s sha256 changed during the embedding", ("W-HASH",)),
    ("--limit ignored", "    todo = miss if limit is None else", "    todo = miss if True else", ("W-GO",)),
    ("go flag ignored", "    if not go:\n        print(\"%s dry: nothing posted", "    if False:\n        print(\"%s dry: nothing posted", ("W-REFUSE",)),
    ("preflight texts = the last 20", "    chosen = texts[:PARITY_N]\n", "    chosen = texts[-PARITY_N:]\n", ("W-GO",)),
    ("probe posts RAW", "        embed_fn(ITS.MODEL[e], [PROMPTS[e] + t for t in sub[s:s + EA.BATCH]])\n", "        embed_fn(ITS.MODEL[e], sub[s:s + EA.BATCH])\n", ("W-DRY",)),
    ("qwen3 LF check removed", "    if q.count(\"\\n\") != 1 or", "    if False and q.count(\"\\n\") != 1 or", ("W-CONST", "W-T0")),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="cpw_mut_")
    with _scope({"pins": None}):
        fx = build_fixture(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        code = head.replace(old, new)
        ns = {"__name__": "cpw_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=fx)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        finally:
            for d in os.listdir(td):
                if os.path.isdir(os.path.join(td, d)):
                    shutil.rmtree(os.path.join(td, d), ignore_errors=True)
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
        sys.stdout.flush()
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS (writer): %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-S0-CARD-PROTOCOL writer: card-prompt embeddings over S0's text set (zero judge calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--embed", action="store_true")
    ap.add_argument("--embedder", choices=EMB)
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
    if (a.dry_run or a.embed) and not a.embedder:
        refuse("--dry-run / --embed need --embedder (one of %s)" % (EMB,))
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        return dry_run(a.embedder, a.db, a.emb_dir, probe_n=a.probe_n)
    saved = (EA.PACE_S, EA.TW_DRAIN)
    if a.pace_s is not None or a.tw_drain is not None:
        EA.PACE_S = a.pace_s if a.pace_s is not None else EA.PACE_S
        EA.TW_DRAIN = a.tw_drain if a.tw_drain is not None else EA.TW_DRAIN
        print("%s pacing: pause %s s after each batch; TIME_WAIT drain threshold %s (poll %.0f s, cap %.0f s)"
              % (TAG, EA.PACE_S or "none", EA.TW_DRAIN, EA.TW_POLL_S, EA.TW_MAX_S))
    try:
        embed(a.embedder, a.go, limit=a.limit, db=a.db, emb_dir=a.emb_dir)
    finally:
        EA.PACE_S, EA.TW_DRAIN = saved
    return 0


if __name__ == "__main__":
    sys.exit(main())
