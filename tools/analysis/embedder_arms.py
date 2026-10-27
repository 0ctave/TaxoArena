"""EMBEDDER-CROSS-FLAT (docs/judge_v2_program.md section "## Registered 2026-09-27 (before any code or call) - EMBEDDER-CROSS-FLAT",
L21705-L21730) with the author's decision (b) of 2026-09-27 (section "## Registrar's record 2026-09-27 ... the author's decisions
(a)-(c)", L21831-L21846): the two extra embedders are nomic-embed-text (v1.5) and embeddinggemma; PRIMARY protocol RAW; the
card-conformant arms a REGISTERED SECONDARY (nomic: "clustering: " prefix plus layer_norm; gemma: "task: clustering | query: ");
gemma's missing texts are embedded. mxbai is NOT an arm (not decided).

What this module is: the ARM TABLE and the WIRING through EMBEDDER-PLUMBING's flag (flat_mix_mmlu.configure_embedding, i.e.
--embedding-cache-file / --embedding-model), plus the PRE-EMBEDDER that (i) embeds the texts missing from gemma's raw cache and
(ii) writes the card-conformant per-model files. ZERO judge calls. The pre-embedder posts EMBEDDING requests to the local Ollama
server ONLY under --embed-* ... --go; it was NOT run by its builder (the orchestrator's instruction: add the code, do not run it).

Arms (file names by embedder_guard.cache_file_for, EmbeddingCache.cacheFileFor's rule; the card files add "__card"):
  qwen3_raw   qwen3-embedding:latest   embeddings_cache.db (the DB of record; NO flag: ruling R2)
  nomic_raw   nomic-embed-text:latest  embeddings_cache_nomic-embed-text_latest.db         PRIMARY
  nomic_card  nomic-embed-text:latest  embeddings_cache_nomic-embed-text_latest__card.db   SECONDARY  prefix "clustering: ", layer_norm
  gemma_raw   embeddinggemma:latest    embeddings_cache_embeddinggemma_latest.db           PRIMARY
  gemma_card  embeddinggemma:latest    embeddings_cache_embeddinggemma_latest__card.db     SECONDARY  prefix "task: clustering | query: "
A card file stores, under the RAW text as its key (the readers join on the raw text), the model's vector of PREFIX + text after
the card's transform (nomic: layer_norm over the full native vector, no affine, eps 1e-5); the readers then slice to 256 and
renormalise, which completes the card's recipe (nomic v1.5: layer_norm -> truncate -> L2; gemma: MRL truncate -> L2).

Guards: every non-qwen3 arm goes through configure_embedding (the explicit flag: validate_cache_file) with the model named
explicitly; reading an arm REFUSES unless every needed text has a vector of exactly the model's native dimension
(embedder_guard.NATIVE_DIM), printed per arm (arm_read_guard). The vmfMu guard (embedder_guard.guard_file through
flat_mix_mmlu.embedding_guard_flat) applies where a TREE of that embedder exists (E1: the nomic build); E0b fits flat partitions in a
space with no tree of its own, so there is no vmfMu to check against (reported to the registrar; not resolved here).

Writes (only with --go): the pre-embedder refuses a target with a non-empty -wal / -journal (the steward checkpoints first), prints
the target's sha256 before and after, never touches embeddings_cache.db (refused by name), inserts with INSERT OR IGNORE, and refuses
unless the missing count equals --expect-missing (the registration's 3,520 for gemma raw; printed, never assumed).
write_vectors opens the target with sqlite3.connect._raw when present, i.e. it deliberately BYPASSES the harness's read-only
connect patch (it is the one writer; the DB of record is refused by name first) (READY_w0_delta1 C8-3 LOW).

Route parity (READY_w0_delta1 C8-3): the existing raw rows came through the engine's langchain4j route, the new ones come from
/api/embed. Under --embed-missing ... --go, BEFORE any write, route_parity re-embeds PARITY_N = 20 texts already in the target
(the first 20 by sha256 of the text) through the same embed function and requires MIN cos >= PARITY_COS = 0.9999 after
slice-to-256 and renormalise; it prints "[EMB-ARMS] route parity ..." and REFUSES (nothing written) below the bar or with fewer
than 20 existing rows. The dry run posts nothing and so does not run it. embed_card(go=False) posts and writes nothing (C8-2,
selftest EA-CARD).

Connect guard (delta w0-delta3, 2026-09-29): needed_texts() imports flat_mix_mmlu, whose connect guard then sits on
sqlite3.connect and admits four DB names only; on main 481b613 the gemma_raw --go refused before any write ("... is not a DB this
test reads"). Every read of an arm file now goes through open_arm_ro(path, arm): the path's name must be THAT arm's cache file
(else REFUSED), and exactly that one name is admitted to the guard for the duration of the open, then the guard's tuple is
restored; the guard's -wal / -journal rule still binds (an uncheckpointed gemma -wal still REFUSES: C8-5). Selftest EA-FMGUARD
runs the pre-embedder under the REAL guard on stub DBs (mutants: admission removed, outliving the open, every arm admitted,
name check dropped, card source unadmitted: 5 of 5 KILLED).

[2026-09-29, the engine-coder, EMB-TARGET-DIR; insertion only] --target-dir DIR (with --embed-missing / --embed-card only; any
other mode REFUSES). Why: the gemma_raw --go write to the shared repo-root cache was denied by the permission system (run log
532dd1d); the author cannot approve writes to the shared caches today. With the flag the pre-embedder writes ONLY to
DIR/<the arm's cache file name> (cache_file's rule, the same basename): a raw arm's source (DATA_ROOT/<basename>) is COPIED
byte-for-byte (sha256 of the copy == the source's, before and after the copy, else REFUSED) and the missing vectors inserted
into the copy; a card arm's file is created NEW in DIR (the queries rows from the raw source). The source's sha256 is printed
(dry and --go) and recorded in DIR/<basename>.provenance.json (mode x: arm, source + sha256, copy + sha256 after the write,
vectors written, this script's LF blob); a source whose sha256 changed during the run REFUSES the provenance. REFUSED before any
post: DIR absent; DIR = the source's directory (realpath + normcase; the source is never a target); the copy or its provenance
already in DIR (one fresh copy per DIR); the source absent; a non-empty -wal / -journal beside the source. Kept: the -wal
refusal on the target (write_vectors), route parity (on the SOURCE, read-only, BEFORE the copy: a FAIL leaves DIR empty),
--expect-missing (counted on the source), qwen3 refused by name, the "sha256 before / after" lines (the copy's before = the
source's). The dry run copies and posts nothing.
Reader (EMBEDDER-CROSS-FLAT): configure_arm(FM, arm, data_root, target_dir=DIR) reads the copy and ONLY it: DIR/<basename> with
a provenance naming THIS path and arm whose sha256_after equals the file's sha256 now, then flat_mix_mmlu.configure_embedding
(explicit file and model; the connect guard admits the basename; the embedder guard reads the copy) and pin_copy_connect: any
open of a file with that basename that is not the copy (the source under DATA_ROOT) REFUSES. qwen3, DIR = the data root, a
moved or modified copy, and an arm with no copy in DIR REFUSE. flat_mix_mmlu.py / embedder_guard.py are NOT changed (pinned by
flat_generality.py FLAT_MIX_PIN and flat_mix IMPORT_PINS). Flag absent: byte-identical behaviour (--inertness: the base blob
4f56e79d of main 532dd1d vs this file on the same modes, stdout / refusals / file sha256s / stub requests identical, with the
execution discriminator); --help gains the flag's line (the only difference). Selftests EA-TARGET (main(argv) end to end
through a STUB Ollama over HTTP) and EA-TREADER (the real flat_mix connect guard and embedder guard); mutants TD-*.
  python tools/analysis/embedder_arms.py --inertness
  python tools/analysis/embedder_arms.py --embed-missing gemma_raw --expect-missing N --target-dir DIR          # dry
  python tools/analysis/embedder_arms.py --embed-missing gemma_raw --expect-missing N --target-dir DIR --go
  python tools/analysis/embedder_arms.py --embed-card gemma_card --target-dir DIR --go    # nomic_card likewise
  (N = the missing count the dry run prints; run log 532dd1d: the dry run passed at 3504; the registration's figure is 3,520)

[2026-09-29, the engine-coder, EMB-TARGET2 after READY_emb_target 6202766; insertion only, the text above stands]
C-ET-1: the raw copy is CREATED exclusively (open 'xb', _copy_exclusive) and the NEW card file too (open 'xb' under --go, before
any post); a file that appears at the copy path after target_paths' check REFUSES and is left untouched (EA-TARGET plants one
during the parity / after the check). C-ET-3: open_arm_reader(FM, arm, DIR) is THE EMBEDDER-CROSS-FLAT (E0b) reader entry: qwen3
with no flag (R2); every other arm ONLY through configure_arm(target_dir=DIR); no DIR REFUSES. flat_mix_mmlu.configure_embedding
now REFUSES an arm file (a __card.db, a file with a provenance beside it, or any file under DATA_ROOT/experiment_results/
embedder_cross) unless configure_arm_copy names that one path (flat_mix.ARM_COPY_ADMITTED, set for the call and cleared), so
flat_mix --embedding-cache-file <DIR copy> REFUSES (EA-TREADER, flat_mix FT-EMBGUARD). C-ET-4: configure_arm_copy also checks
the REGISTRAR's pin (registrar_pin; experiment_configs/embedder_cross_arm_pins.json, schema embedder_cross_arm_pins/v1): the file
absent, another schema, the arm's sha256 null (committed state: every arm null, so every read REFUSES until the registrar
brackets the pins after the --go runs) or different REFUSES. nomic_raw is read from its own DIR copy too (made by
--embed-missing nomic_raw --expect-missing <its dry-run count> --target-dir DIR --go; 0 missing posts only the 20 parity texts).

[2026-09-29, the engine-coder, EMB-CONN after the W1 / W2 incidents (run log 2332d29); insertion only, the text above stands]
(a) ONE persistent HTTP/1.1 keep-alive connection per server (OllamaClient via http.client; reopened only after a transient
failure or a server-side close), replacing urllib's connection per request. (b) A BOUNDED retry: 5 retries with backoff
2 / 8 / 30 / 60 / 120 s (220 s, beyond Windows' 120 s TIME_WAIT) on transient CONNECTION errors only (OSError incl.
ConnectionError / TimeoutError / WinError 10048, http.client.HTTPException incl. RemoteDisconnected, and an HTTP 400/500/502/503
whose body names a socket-level failure, e.g. W2's "connectex: Only one usage of each socket address"); any other HTTP error,
a count mismatch and a dimension mismatch REFUSE at once, never retried. A batch is posted whole, retried whole and inserted only
after its whole response passed the count check, so a batch is never half-written; after the last retry the run REFUSES with
the earlier batches whole (the partial file carries no provenance, so every reader refuses it; the operator removes it).
(c) I-2: client_base() turns OLLAMA_HOST's server bind form (0.0.0.0, ::, :port, a bare host) into a client URL
(http://127.0.0.1:11434 by default). NOTE: W2's TIME_WAIT sockets were mostly Ollama's OWN server->runner dials (the 400 body is
the server failing to dial its runner's /tokenize); (a) removes the client's share only, (b) is what rides the exhaustion out.
Selftest EA-CONN on the stub Ollama (HTTP/1.1, connection counter, injectable faults).

[2026-09-30, the engine-coder, EMB-PACE after the INTENT-TRANSFER-S0 qwen3 --go incident (log
experiment_results/intent_transfer_s0/embed/embed_qwen3_go.log, main 6885f92); insertion only, the text above stands]
(a) Ollama answered HTTP 400 "... dial tcp 127.0.0.1:<port>: bind: An operation on a socket could not be performed because the
system lacked sufficient buffer space or because a queue was full." (WSAENOBUFS, WinError 10055: the same ephemeral-port
exhaustion inside Ollama's own /tokenize dials as W2), and it was REFUSED as non-transient. TRANSIENT_BODY now also names
"lacked sufficient buffer space", "queue was full", "WSAENOBUFS" and "10055": the same bounded whole-batch retry, the same
refusal after the 5th retry, no other HTTP error made transient. (b) OPTIONAL pacing, both OFF by default (PACE_S = 0.0,
TW_DRAIN = None): with PACE_S > 0, write_vectors sleeps PACE_S after each committed batch; with TW_DRAIN = N, after the backoff of
a transient error ollama_embed polls the host's TIME_WAIT socket count (time_wait_count: PowerShell Get-NetTCPConnection -State
TimeWait; None when it cannot be read) every TW_POLL_S until it is below N, for at most TW_MAX_S, then retries the whole batch
(an unreadable count waits TW_MAX_S once, printed). Absent flags: no extra sleep, no probe, the request sequence and the written
rows unchanged (selftest EA-PACE: the no-flag leg makes 0 probe calls and the pre-change sleep sequence; the flag legs show the
pauses and the drain executed). Callers set the two module values (intent_transfer_s0.py --pace-s / --tw-drain); this module's
own CLI is unchanged.

Launch sequence (run-operator, in a W2 window after THREAD-CAP and EMBEDDER-PLUMBING merge, backup first):
  python tools/analysis/embedder_arms.py --selftest
  python tools/analysis/embedder_arms.py --mutants
  python tools/analysis/embedder_arms.py --plan                                   # counts only: needed texts, missing per arm
  python tools/analysis/embedder_arms.py --embed-missing gemma_raw --expect-missing 3520          # dry: prints, posts nothing
  python tools/analysis/embedder_arms.py --embed-missing gemma_raw --expect-missing 3520 --go     # posts embedding requests
  python tools/analysis/embedder_arms.py --embed-card nomic_card --go ; ... --embed-card gemma_card --go
Ollama thread cap: route (ii), tools/ollama_affinity.ps1 -Threads 12 -Apply before the first request (THREAD-CAP).
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:                       # BEFORE numpy
    os.environ[_v] = "1"

import sys
import json
import struct
import sqlite3
import hashlib
import shutil
import argparse
import tempfile
import contextlib
import urllib.request
import urllib.parse
import http.client
import time
from collections import namedtuple

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pool_guard          # noqa: E402
import embedder_guard as EG  # noqa: E402

TAG = "[EMB-ARMS]"
POOL_ID = "p2dca21ab5f4ef3ae"


def client_base(host=None):
    """I-2 (incident W1, run log 2332d29): OLLAMA_HOST is the SERVER's bind form for Ollama ("0.0.0.0", ":11434", a bare
    host[:port]); the client needs a URL. Unset / empty -> http://127.0.0.1:11434; no scheme -> http://; a bind-all host
    (0.0.0.0, ::) -> 127.0.0.1; no port -> 11434. A full URL with a real host is kept (its trailing slash dropped)."""
    h = (os.environ.get("OLLAMA_HOST", "") if host is None else host).strip().rstrip("/")
    if not h:
        return "http://127.0.0.1:11434"
    if "://" not in h:
        h = "http://" + h
    u = urllib.parse.urlsplit(h)
    name = u.hostname or ""
    if name in ("", "0.0.0.0", "::"):
        name = "127.0.0.1"
    elif ":" in name:
        name = "[%s]" % name
    return "%s://%s:%d" % (u.scheme or "http", name, u.port or 11434)


OLLAMA_URL = client_base() + "/api/embed"
BATCH = 32
PARITY_N = 20
PARITY_COS = 0.9999
PARITY_SLICE = 256
LN_EPS = 1e-5

Arm = namedtuple("Arm", "name model role prefix layer_norm")
ARMS = {a.name: a for a in (
    Arm("qwen3_raw", "qwen3-embedding:latest", "REFERENCE", "", False),
    Arm("nomic_raw", "nomic-embed-text:latest", "PRIMARY", "", False),
    Arm("nomic_card", "nomic-embed-text:latest", "SECONDARY", "clustering: ", True),
    Arm("gemma_raw", "embeddinggemma:latest", "PRIMARY", "", False),
    Arm("gemma_card", "embeddinggemma:latest", "SECONDARY", "task: clustering | query: ", False),
)}


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def cache_file(arm):
    """The arm's cache file name (DATA_ROOT-relative): the raw arms by EmbeddingCache.cacheFileFor's rule, the card arms '__card'."""
    base = EG.cache_file_for(arm.model)
    return base[:-3] + "__card.db" if arm.role == "SECONDARY" else base


def is_card(arm):
    return arm.role == "SECONDARY"


def card_transform(arm, v):
    """The card's transform applied BEFORE storage (the readers slice to 256 and renormalise afterwards)."""
    v = np.asarray(v, dtype=np.float64)
    if arm.layer_norm:
        return (v - v.mean()) / np.sqrt(v.var() + LN_EPS)
    return v


def configure_arm(FM, arm, data_root, target_dir=None):
    """Wire the arm through EMBEDDER-PLUMBING's flag: the DB of record needs no flag (ruling R2); any other arm names its file AND
    its model explicitly (configure_embedding validates the file fail-closed). target_dir (EMB-TARGET-DIR): the arm is read from
    the pre-embedder's --target-dir copy and ONLY that copy (configure_arm_copy); None -> the code below, unchanged."""
    if target_dir is not None:
        return configure_arm_copy(FM, arm, data_root, target_dir)
    if arm.name == "qwen3_raw":
        return None
    path = os.path.join(data_root, cache_file(arm))
    FM.configure_embedding(cache_file=path, model=arm.model)
    return path


def arm_read_guard(con, arm, texts):
    """Every needed text has a vector of exactly the model's native dimension; prints and REFUSES otherwise."""
    native = EG.NATIVE_DIM[EG.canonical_model(arm.model)]
    want, dims, have = set(texts), {}, set()
    for t, blob in con.execute("SELECT query, vector FROM embeddings"):
        if t in want and isinstance(blob, bytes):
            n = len(blob) // 4
            dims[n] = dims.get(n, 0) + 1
            have.add(t)
    missing = len(want - have)
    print("%s arm %s (%s, %s): %d of %d needed texts have a vector; raw dims %s; native %d"
          % (TAG, arm.name, arm.model, arm.role, len(have), len(want), dict(sorted(dims.items())), native))
    if missing or set(dims) - {native}:
        refuse("arm %s: %d needed texts missing, dims %s != {%d}" % (arm.name, missing, dict(sorted(dims.items())), native))
    return len(have)


def missing_texts(con, texts):
    have = set(t for (t,) in con.execute("SELECT query FROM embeddings"))
    return sorted(set(texts) - have)


# EMB-CONN (incident W2, run log 2332d29: 14,922 sockets in TIME_WAIT, HTTP 400 "Only one usage of each socket address" at
# batch 66): ONE persistent keep-alive connection per server for every request (OllamaClient), and a BOUNDED retry with
# backoff on transient CONNECTION errors only (never on a count / dimension mismatch, never on another HTTP error). A batch
# is posted whole, retried whole, and inserted only after its whole response passed the count check, so a batch is never
# half-written; after the last retry the run REFUSES.
RETRY_BACKOFF_S = (2.0, 8.0, 30.0, 60.0, 120.0)    # 5 retries, 220 s in all: beyond Windows' 120 s TIME_WAIT
TRANSIENT_BODY = ("Only one usage of each socket address", "connectex", "connection refused", "connection reset",
                  "EOF", "broken pipe",
                  "lacked sufficient buffer space", "queue was full", "WSAENOBUFS", "10055")     # EMB-PACE (a): WSAENOBUFS
_sleep = time.sleep                                # module-level so the selftest can record the backoff
PACE_S = 0.0                                       # EMB-PACE (b): fixed pause after each committed batch; 0 = off
TW_DRAIN = None                                    # EMB-PACE (b): after a transient error, wait for TIME_WAIT < N; None = off
TW_POLL_S, TW_MAX_S = 10.0, 600.0


def time_wait_count():
    """The host's TCP TIME_WAIT socket count (locale-independent: PowerShell Get-NetTCPConnection); None if unreadable."""
    try:
        import subprocess
        if os.name == "nt":
            out = subprocess.run(["powershell", "-NoProfile", "-Command",
                                  "(Get-NetTCPConnection -State TimeWait -ErrorAction SilentlyContinue | Measure-Object).Count"],
                                 capture_output=True, text=True, timeout=60).stdout
        else:
            out = str(sum(1 for ln in subprocess.run(["ss", "-tan", "state", "time-wait"], capture_output=True, text=True,
                                                     timeout=60).stdout.splitlines()[1:] if ln.strip()))
        return int(out.strip())
    except Exception:                                  # noqa: BLE001
        return None


_tw_count = time_wait_count                        # module-level so the selftest substitutes a stub


def drain_time_wait(threshold):
    """EMB-PACE (b): poll until TIME_WAIT < threshold (every TW_POLL_S, at most TW_MAX_S); an unreadable count waits TW_MAX_S once."""
    waited = 0.0
    while True:
        n = _tw_count()
        if n is None:
            print("%s TIME_WAIT count unreadable: waiting %.0f s once" % (TAG, TW_MAX_S))
            _sleep(TW_MAX_S)
            return None
        if n < threshold or waited >= TW_MAX_S:
            print("%s TIME_WAIT %d (threshold %d) after %.0f s of draining%s" % (TAG, n, threshold, waited,
                                                                                "" if n < threshold else ": cap reached, retrying anyway"))
            return n
        _sleep(TW_POLL_S)
        waited += TW_POLL_S
_CLIENTS = {}


class OllamaClient(object):
    """One http.client.HTTPConnection (HTTP/1.1 keep-alive) reused for every POST; reopened only after a transient failure or a
    server-side close. `opened` counts the TCP connections this client made."""

    def __init__(self, base):
        u = urllib.parse.urlsplit(base)
        self.scheme, self.host, self.port = u.scheme or "http", u.hostname, u.port or 11434
        self.conn, self.opened = None, 0

    def reset(self):
        if self.conn is not None:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def post(self, path, body):
        if self.conn is None:
            cls = http.client.HTTPSConnection if self.scheme == "https" else http.client.HTTPConnection
            self.conn = cls(self.host, self.port, timeout=600)
            self.opened += 1
        self.conn.request("POST", path, body=body, headers={"Content-Type": "application/json", "Connection": "keep-alive"})
        r = self.conn.getresponse()
        data = r.read()
        if r.will_close:
            self.reset()
        return r.status, data


def client_for(url):
    u = urllib.parse.urlsplit(url)
    base = "%s://%s" % (u.scheme or "http", u.netloc)
    if base not in _CLIENTS:
        _CLIENTS[base] = OllamaClient(base)
    return _CLIENTS[base], (u.path or "/api/embed")


def close_clients():
    for c in _CLIENTS.values():
        c.reset()
    _CLIENTS.clear()


def _transient_http(status, text):
    return status in (400, 500, 502, 503) and any(t.lower() in text.lower() for t in TRANSIENT_BODY)


def ollama_embed(model, inputs, url=None):
    """One POST to Ollama /api/embed (an EMBEDDING request, never a judge call) over the persistent connection. -> list of
    vectors. url None -> the module's OLLAMA_URL read at CALL time (the selftest points it at a stub Ollama on 127.0.0.1)."""
    url = OLLAMA_URL if url is None else url
    body = json.dumps({"model": model, "input": list(inputs)}).encode("utf-8")
    client, path = client_for(url)
    out = None
    for attempt in range(len(RETRY_BACKOFF_S) + 1):
        try:
            status, data = client.post(path, body)
        except (OSError, http.client.HTTPException) as e:        # ConnectionError, TimeoutError, WinError 10048, RemoteDisconnected
            client.reset()
            why = "%s: %s" % (type(e).__name__, e)
        else:
            if status == 200:
                out = json.loads(data.decode("utf-8"))
                break
            text = data.decode("utf-8", "replace")[:300]
            if not _transient_http(status, text):
                refuse("Ollama HTTP %d on %d inputs: %s (not a transient connection error: no retry)" % (status, len(inputs), text))
            client.reset()
            why = "HTTP %d: %s" % (status, text)
        if attempt == len(RETRY_BACKOFF_S):
            refuse("Ollama: %d attempts of one batch of %d inputs failed on transient connection errors; the batch is NOT written "
                   "(earlier batches are whole): %s" % (attempt + 1, len(inputs), why))
        print("%s transient connection error on a batch of %d inputs (%s); retrying the WHOLE batch in %.0f s (%d of %d)"
              % (TAG, len(inputs), why[:160], RETRY_BACKOFF_S[attempt], attempt + 1, len(RETRY_BACKOFF_S)))
        _sleep(RETRY_BACKOFF_S[attempt])
        if TW_DRAIN is not None:
            drain_time_wait(TW_DRAIN)
    embs = out.get("embeddings")
    if not isinstance(embs, list) or len(embs) != len(inputs):
        refuse("Ollama returned %s embeddings for %d inputs" % (len(embs) if isinstance(embs, list) else None, len(inputs)))
    return embs


def raw_arm_of(arm):
    """The PRIMARY (raw) arm of arm's model: the source of a card file's queries rows."""
    return [a for a in ARMS.values() if a.model == arm.model and a.role == "PRIMARY"][0]


@contextlib.contextmanager
def _admit_arm_file(path, arm):
    """RP08 delta 2026-09-29 (w0-delta3): flat_mix_mmlu's connect guard (installed on sqlite3.connect when flat_mix_mmlu is
    imported, e.g. by needed_texts) admits four DB names; an arm cache file is not one of them, so the pre-embedder's own reads
    were refused on main 481b613. This admits EXACTLY the selected arm's file name, only for the duration of one open, and
    restores the guard's tuple afterwards; the guard's other rules (file: URI, mode=ro, a non-empty -wal / -journal refused,
    immutable=1) still apply to it. A path whose name is not the arm's file REFUSES. No-op when flat_mix_mmlu is not imported."""
    base = os.path.basename(path)
    if base != cache_file(arm):
        refuse("open of %s as arm %s: the arm's file is %s" % (base, arm.name, cache_file(arm)))
    fm = sys.modules.get("flat_mix_mmlu")
    saved = None if fm is None else fm.ALLOWED_DB_BASENAMES
    if fm is not None and base not in saved:
        fm.ALLOWED_DB_BASENAMES = saved + (base,)
    try:
        yield
    finally:
        if fm is not None:
            fm.ALLOWED_DB_BASENAMES = saved


def open_arm_ro(path, arm):
    """pool_guard.open_ro of ONE arm's cache file, admitted through flat_mix_mmlu's connect guard for this open only."""
    with _admit_arm_file(path, arm):
        return pool_guard.open_ro(path)


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _check_target(path):
    if os.path.basename(path) == EG.DB_OF_RECORD:
        refuse("the pre-embedder never writes the DB of record (%s)" % path)
    for sfx in ("-wal", "-journal"):
        sp = path + sfx
        if os.path.exists(sp) and os.path.getsize(sp) > 0:
            refuse("%s is non-empty: the data-steward checkpoints before any write" % sp)


# ------------------------------------------------------------------------------------------------ --target-dir (EMB-TARGET-DIR)
PROVENANCE_SUFFIX = ".provenance.json"
def _copy_exclusive(source, copy):
    """C-ET-1: the copy is CREATED exclusively (open 'xb', O_EXCL): a file that appeared at the copy path after target_paths'
    check (a race) is never overwritten; FileExistsError propagates to stage_copy's refusal."""
    with open(source, "rb") as s, open(copy, "xb") as d:
        shutil.copyfileobj(s, d, 1 << 20)


_copyfile = _copy_exclusive          # module-level so the selftest can substitute a corrupting copy (the verification's witness)
# C-ET-4 (ruling 19, PINS OWED): the registrar's pin file; the reader refuses unless the arm's copy has exactly this sha256.
ROOT = os.path.dirname(os.path.dirname(HERE))
ARM_PINS_FILE = os.path.join(ROOT, "experiment_configs", "embedder_cross_arm_pins.json")
ARM_PINS_SCHEMA = "embedder_cross_arm_pins/v1"


def _norm(p):
    return os.path.normcase(os.path.realpath(os.path.abspath(p)))


def _check_source(path):
    """The -wal / -journal refusal on the SOURCE of a copy: a copy of the main file alone would drop an uncheckpointed tail."""
    for sfx in ("-wal", "-journal"):
        sp = path + sfx
        if os.path.isfile(sp) and os.path.getsize(sp) > 0:
            refuse("%s is non-empty: the data-steward checkpoints the source before it is copied" % sp)


def target_paths(arm, root, target_dir):
    """--target-dir DIR -> (source, copy). copy = DIR/<the arm's cache file name> (cache_file's rule, the same basename); source =
    the raw arm's file under root (a raw arm: the file copied; a card arm: the file whose queries rows the NEW card file takes).
    REFUSES: DIR absent or not a directory; DIR is the source's directory (the source is never a target); the copy or its
    provenance already exists (one fresh copy per DIR); the source absent; a non-empty -wal / -journal beside the source."""
    if not os.path.isdir(target_dir):
        refuse("--target-dir %s is not an existing directory" % target_dir)
    if _norm(target_dir) == _norm(root):
        refuse("--target-dir %s is the source directory %s: the source is never a target" % (target_dir, root))
    copy = os.path.join(os.path.abspath(target_dir), cache_file(arm))
    source = os.path.join(root, cache_file(raw_arm_of(arm)))
    for q in (copy, copy + PROVENANCE_SUFFIX):
        if os.path.lexists(q):
            refuse("%s exists: a --target-dir copy is written once (remove it, or name another DIR)" % q)
    if not os.path.isfile(source):
        refuse("--target-dir: the source %s is absent" % source)
    _check_source(source)
    return source, copy


def resolve_target(arm, root, target_dir):
    """None without --target-dir (the pre-existing path, unchanged); else target_paths(...), printed with the source's sha256."""
    if target_dir is None:
        return None
    source, copy = target_paths(arm, root, target_dir)
    print("%s --target-dir: source %s sha256 %s -> %s %s (absent; written only with --go)"
          % (TAG, source, _sha(source), "copy" if not is_card(arm) else "NEW card file", copy))
    return source, copy


def stage_copy(source, copy):
    """Copy source -> copy (the raw arms); REFUSES unless sha256(copy) == sha256(source) before and after the copy."""
    sha_src = _sha(source)
    try:
        _copyfile(source, copy)
    except FileExistsError:
        refuse("%s appeared after the --target-dir check: the exclusive create refused it; that file is left untouched (C-ET-1)" % copy)
    sha_copy, sha_src2 = _sha(copy), _sha(source)
    if not (sha_copy == sha_src == sha_src2):
        refuse("copy %s sha256 %s != source sha256 %s (after the copy %s)" % (copy, sha_copy, sha_src, sha_src2))
    print("%s copied %s -> %s; sha256 %s (copy == source, verified)" % (TAG, source, copy, sha_copy))
    return sha_src


def _script_blob():
    with open(os.path.abspath(__file__), "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def model_digest(model, url=None):
    """C-E0B-7 (READY_emb_e0b cd85961): the Ollama tag digest of [model] from /api/tags at the --go (a local listing, not an
    embedding, never a judge call); None when the server does not answer or does not list the model."""
    base = (OLLAMA_URL if url is None else url)
    base = base[:-len("/api/embed")] if base.endswith("/api/embed") else base
    try:
        with urllib.request.urlopen(base + "/api/tags", timeout=10) as r:
            models = json.loads(r.read().decode("utf-8")).get("models") or []
    except Exception:                                   # noqa: BLE001  (recorded UNAVAILABLE)
        return None
    for m in models:
        if model in (m.get("name"), m.get("model")):
            return m.get("digest")
    return None


def write_provenance(copy, arm, source, source_sha, n):
    """After the write: REFUSES unless the source is byte-unchanged (sha256 == source_sha), then writes
    <copy>.provenance.json once (mode x): the arm, the source and its sha256, the copy and its sha256 after the write."""
    now = _sha(source)
    if now != source_sha:
        refuse("the source %s changed during the run: sha256 %s != %s recorded before (a write reached the source)" % (source, now, source_sha))
    rec = dict(arm=arm.name, model=arm.model, role=arm.role, copy=os.path.abspath(copy), copy_basename=os.path.basename(copy),
               source=os.path.abspath(source), source_sha256=source_sha,
               source_use="copied byte-for-byte, then the missing vectors inserted" if not is_card(arm)
               else "queries rows copied into a NEW card file", vectors_written=n, sha256_after=_sha(copy),
               script="tools/analysis/embedder_arms.py blob:%s (LF)" % _script_blob(),
               model_digest=model_digest(arm.model) or "UNAVAILABLE")
    with open(copy + PROVENANCE_SUFFIX, "x", encoding="utf-8") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print("%s provenance %s: arm %s, source sha256 %s (unchanged), copy sha256 after %s; model digest %s"
          % (TAG, copy + PROVENANCE_SUFFIX, arm.name, source_sha, rec["sha256_after"], rec["model_digest"]))
    return rec


def pin_copy_connect(path):
    """The reader side: on top of whatever sqlite3.connect is (flat_mix_mmlu's connect guard admits by BASENAME), any open of a
    file with the copy's basename that is not the copy itself REFUSES (the source under DATA_ROOT has the same name). ._raw kept."""
    base, want, prev = os.path.basename(path), _norm(path), sqlite3.connect

    def pinned(database, *a, **k):
        s = str(database)
        p = s[5:].partition("?")[0] if s.startswith("file:") else s
        if os.path.basename(p) == base and _norm(p) != want:
            refuse("sqlite3.connect(%r): under --target-dir only the copy %s is read as %s" % (s, path, base))
        return prev(database, *a, **k)
    pinned._raw = getattr(prev, "_raw", prev)
    pinned._pinned_copy = path
    sqlite3.connect = pinned
    return prev


def configure_arm_copy(FM, arm, data_root, target_dir):
    """EMBEDDER-CROSS-FLAT's reader on a --target-dir copy: DIR/<the arm's cache file>, with its provenance naming THIS path and
    its sha256 after the write equal to the file's sha256 now; then configure_embedding (the explicit file and model, validated;
    the connect guard admits the basename) and the path pin (pin_copy_connect). Everything else REFUSES."""
    if arm.name == "qwen3_raw":
        refuse("qwen3_raw is the DB of record (%s): read in place with no flag, never through a --target-dir copy" % EG.DB_OF_RECORD)
    if _norm(target_dir) == _norm(data_root):
        refuse("--target-dir %s is the source directory: the reader reads the copy, never the source" % target_dir)
    path = os.path.join(os.path.abspath(target_dir), cache_file(arm))
    pv = path + PROVENANCE_SUFFIX
    if not (os.path.isfile(path) and os.path.isfile(pv)):
        refuse("no --target-dir copy of arm %s at %s (file %s, provenance %s)" % (arm.name, path, os.path.isfile(path), os.path.isfile(pv)))
    with open(pv, encoding="utf-8") as f:
        rec = json.load(f)
    if rec.get("arm") != arm.name or rec.get("copy_basename") != cache_file(arm) or _norm(rec.get("copy") or "") != _norm(path):
        refuse("the provenance %s names arm %r at %r, not arm %s at %s" % (pv, rec.get("arm"), rec.get("copy"), arm.name, path))
    sha = _sha(path)
    if sha != rec.get("sha256_after"):
        refuse("the copy %s sha256 %s != the provenance's sha256_after %s (modified after the pre-embedder wrote it)"
               % (path, sha, rec.get("sha256_after")))
    registrar_pin(arm, sha)
    print("%s reader: arm %s reads the --target-dir copy %s sha256 %s (== provenance == the registrar's pin; source %s sha256 %s)"
          % (TAG, arm.name, path, sha, rec.get("source"), rec.get("source_sha256")))
    FM.ARM_COPY_ADMITTED = os.path.abspath(path)        # C-ET-3: the one path flat_mix's arm-copy gate admits, for this call
    try:
        FM.configure_embedding(model=arm.model, cache_file=path)
    finally:
        FM.ARM_COPY_ADMITTED = None
    pin_copy_connect(path)
    return path


def registrar_pin(arm, sha, pins_file=None):
    """C-ET-4 (ruling 19): the REGISTRAR's pin, not the writer's provenance. REFUSES: the pin file absent or unreadable; a
    schema other than ARM_PINS_SCHEMA; the arm absent; its sha256 not yet bracketed (null); a sha256 other than the file's."""
    pf = ARM_PINS_FILE if pins_file is None else pins_file
    if not os.path.isfile(pf):
        refuse("the registrar's pin file %s is absent (ruling 19: no arm is read before its pin is bracketed)" % pf)
    try:
        with open(pf, encoding="utf-8") as f:
            pins = json.load(f)
    except ValueError as e:
        refuse("the registrar's pin file %s is not JSON (%s)" % (pf, e))
    if not isinstance(pins, dict) or pins.get("schema") != ARM_PINS_SCHEMA or not isinstance(pins.get("arms"), dict):
        refuse("the registrar's pin file %s: schema %r, expected %r with an 'arms' map" % (pf, (pins or {}).get("schema")
                                                                                         if isinstance(pins, dict) else None, ARM_PINS_SCHEMA))
    ent = pins["arms"].get(arm.name)
    want = ent.get("sha256") if isinstance(ent, dict) else None
    if not want:
        refuse("the registrar's pin file %s has no sha256 for arm %s yet (ruling 19, PINS OWED)" % (pf, arm.name))
    if want != sha:
        refuse("arm %s: the file's sha256 %s != the registrar's pin %s (%s)" % (arm.name, sha, want, pf))
    print("%s registrar pin: arm %s sha256 %s == %s" % (TAG, arm.name, sha, os.path.basename(pf)))
    return want


def open_arm_reader(FM, arm_name, target_dir, data_root=None):
    """THE EMBEDDER-CROSS-FLAT (E0b) reader entry (C-ET-3): qwen3_raw -> the DB of record with no flag (ruling R2, None);
    every other arm ONLY through configure_arm(FM, arm, DATA_ROOT, target_dir=DIR) (copy-only, provenance, registrar pin,
    path pin, flat_mix's arm-copy gate). A non-qwen3 arm without a DIR REFUSES (no root read, no --embedding-cache-file)."""
    arm = ARMS[arm_name]
    if arm.name == "qwen3_raw":
        return configure_arm(FM, arm, data_root if data_root is not None else pool_guard.DATA_ROOT)
    if target_dir is None:
        refuse("arm %s is read only from its --target-dir copy (EMBEDDER-CROSS-FLAT; C-ET-3): no DIR given" % arm_name)
    return configure_arm(FM, arm, data_root if data_root is not None else pool_guard.DATA_ROOT, target_dir=target_dir)


def write_vectors(path, arm, texts, embed_fn, queries_src=None):
    """Embed PREFIX + text for each text (batches of BATCH), apply the card transform, and INSERT OR IGNORE under the RAW text.
    Creates the file (schema of EmbeddingCache) when absent; copies the queries rows of [queries_src] when given."""
    _check_target(path)
    native = EG.NATIVE_DIM[EG.canonical_model(arm.model)]
    existed = os.path.exists(path)
    print("%s target %s (%s) sha256 before %s" % (TAG, path, "exists" if existed else "new", _sha(path) if existed else "-"))
    con = getattr(sqlite3.connect, "_raw", sqlite3.connect)(path)
    try:
        con.execute("CREATE TABLE IF NOT EXISTS embeddings (query TEXT PRIMARY KEY, vector BLOB)")
        con.execute("CREATE TABLE IF NOT EXISTS queries (id TEXT PRIMARY KEY, raw_text TEXT, distilled_text TEXT, "
                    "ground_truth_category TEXT DEFAULT '', query_id INTEGER DEFAULT -1)")
        if queries_src is not None:
            src = open_arm_ro(queries_src, raw_arm_of(arm))
            try:
                rows = src.execute("SELECT id, raw_text, distilled_text, ground_truth_category, query_id FROM queries").fetchall()
            finally:
                src.close()
            con.executemany("INSERT OR IGNORE INTO queries VALUES (?, ?, ?, ?, ?)", rows)
        n = 0
        for s in range(0, len(texts), BATCH):
            ch = texts[s:s + BATCH]
            embs = embed_fn(arm.model, [arm.prefix + t for t in ch])
            for t, e in zip(ch, embs):
                if len(e) != native:
                    refuse("model %s returned a %d-d vector (native %d)" % (arm.model, len(e), native))
                v = card_transform(arm, e)
                con.execute("INSERT OR IGNORE INTO embeddings (query, vector) VALUES (?, ?)", (t, struct.pack(">%df" % len(v), *v)))
                n += 1
            con.commit()
            if PACE_S > 0:
                _sleep(PACE_S)
    finally:
        con.close()
    print("%s wrote %d vectors; sha256 after %s" % (TAG, n, _sha(path)))
    return n


def _slice_unit(v, d=PARITY_SLICE):
    v = np.asarray(v, dtype=np.float64)[:d]
    return v / np.linalg.norm(v)


def route_parity(path, arm, embed_fn, n=PARITY_N, bar=PARITY_COS):
    """C8-3: re-embed n texts already stored in [path] through [embed_fn] (the /api/embed route) and compare with the stored
    vectors after slice-to-256 and renormalise; prints min / median cos and REFUSES when min < bar or fewer than n rows exist.
    Returns the min cos. Posts n texts (an embedding request, never a judge call); called only under --go, before any write."""
    if not os.path.exists(path):
        refuse("route parity: %s absent, no existing route to compare against" % path)
    con = open_arm_ro(path, arm)
    try:
        rows = [(t, b) for t, b in con.execute("SELECT query, vector FROM embeddings") if isinstance(b, bytes)]
    finally:
        con.close()
    if len(rows) < n:
        refuse("route parity: %d existing rows in %s < %d" % (len(rows), path, n))
    rows.sort(key=lambda r: hashlib.sha256(r[0].encode("utf-8")).hexdigest())
    rows = rows[:n]
    new = embed_fn(arm.model, [arm.prefix + t for t, _ in rows])
    cos = []
    for (t, b), e in zip(rows, new):
        old = np.array(struct.unpack(">%df" % (len(b) // 4), b))
        cos.append(float(np.dot(_slice_unit(old), _slice_unit(card_transform(arm, e)))))
    mn = min(cos)
    print("%s route parity %s: %d texts re-embedded via /api/embed vs stored rows, cos after slice-%d+renormalise min %.6f "
          "median %.6f (bar >= %.4f): %s" % (TAG, arm.name, len(cos), PARITY_SLICE, mn, float(np.median(cos)), bar,
                                              "PASS" if mn >= bar else "FAIL"))
    if not mn >= bar:
        refuse("route parity %s: min cos %.6f < %.4f; nothing written" % (arm.name, mn, bar))
    return mn


def needed_texts():
    """The texts E0b reads: af_clean_s42's fit set (8,125), the pool's held-out (3,445) and the keyed questions (F6). Reads the DB
    of record read-only (texts only; no statistic)."""
    import flat_mix_mmlu as FM
    texts, _g, _ids, _t = FM.fit_set()
    _train, heldout, _cs = FM.AF.corpus(POOL_ID)
    keyed = FM.F.keyed_questions()
    return sorted(set(texts) | set(t for t, _ in heldout) | set(keyed[3].values()))


# ------------------------------------------------------------------------------------------------ selftest
def selftest(only=None, quiet=False):
    """OLLAMA_URL points at a closed local port for the whole selftest: no real Ollama is contacted (a provenance digest reads
    UNAVAILABLE unless the test serves the stub)."""
    g = globals()
    saved = g["OLLAMA_URL"]
    g["OLLAMA_URL"] = "http://127.0.0.1:9/api/embed"
    try:
        return _selftest(only, quiet)
    finally:
        g["OLLAMA_URL"] = saved


def _selftest(only=None, quiet=False):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    if sel("EA-ARMS"):
        ok([cache_file(ARMS[a]) for a in ("qwen3_raw", "nomic_raw", "nomic_card", "gemma_raw", "gemma_card")] ==
           ["embeddings_cache.db", "embeddings_cache_nomic-embed-text_latest.db", "embeddings_cache_nomic-embed-text_latest__card.db",
            "embeddings_cache_embeddinggemma_latest.db", "embeddings_cache_embeddinggemma_latest__card.db"],
           "EA-ARMS arm files: raw by cacheFileFor's rule, card '__card'")
        ok([(a.role, a.prefix, bool(a.layer_norm)) for a in (ARMS["nomic_raw"], ARMS["nomic_card"], ARMS["gemma_raw"], ARMS["gemma_card"])] ==
           [("PRIMARY", "", False), ("SECONDARY", "clustering: ", True), ("PRIMARY", "", False), ("SECONDARY", "task: clustering | query: ", False)],
           "EA-ARMS raw PRIMARY, card SECONDARY with the card prefixes; layer_norm on nomic card only")
    if sel("EA-LN"):
        v = card_transform(ARMS["nomic_card"], [1.0, 2.0, 3.0, 4.0])
        exp = (np.array([1.0, 2.0, 3.0, 4.0]) - 2.5) / np.sqrt(1.25 + LN_EPS)
        ok(np.allclose(v, exp, atol=1e-12), "EA-LN nomic card layer_norm = (v - mean) / sqrt(var + 1e-5) (%s)" % np.round(v, 6).tolist())
        ok(np.array_equal(card_transform(ARMS["gemma_card"], [1.0, 2.0]), np.array([1.0, 2.0])), "EA-LN gemma card: no transform")
    if sel("EA-WIRE"):
        calls = []

        class FMStub(object):
            @staticmethod
            def configure_embedding(cache_file=None, model=None):
                calls.append((cache_file, model))
        ok(configure_arm(FMStub, ARMS["qwen3_raw"], "R") is None and calls == [], "EA-WIRE qwen3_raw: no flag (the DB of record, ruling R2)")
        configure_arm(FMStub, ARMS["gemma_card"], "R")
        ok(calls == [(os.path.join("R", "embeddings_cache_embeddinggemma_latest__card.db"), "embeddinggemma:latest")],
           "EA-WIRE gemma_card: the explicit file AND the explicit model through configure_embedding")
    with tempfile.TemporaryDirectory() as td:
        posted = []

        def fake(model, inputs):
            posted.append((model, list(inputs)))
            return [[float(len(s)), 1.0] + [0.5] * 766 for s in inputs]
        texts = ["alpha", "beta", "gamma"]
        if sel("EA-WRITE"):
            p = os.path.join(td, "embeddings_cache_nomic-embed-text_latest__card.db")
            wrote = write_vectors(p, ARMS["nomic_card"], texts, fake)
            ok(wrote == 3 and posted[0] == ("nomic-embed-text:latest", ["clustering: alpha", "clustering: beta", "clustering: gamma"]),
               "EA-WRITE nomic_card posts PREFIX + text, 3 vectors written")
            con = pool_guard.open_ro(p)
            try:
                got = {t: np.array(struct.unpack(">768f", b)) for t, b in con.execute("SELECT query, vector FROM embeddings")}
                ok(sorted(got) == texts, "EA-WRITE stored under the RAW text (the readers' join key)")
                e = card_transform(ARMS["nomic_card"], [float(len("clustering: beta")), 1.0] + [0.5] * 766)
                ok(np.allclose(got["beta"], e, atol=1e-5), "EA-WRITE the stored vector is the layer-normed card vector (float32)")
                ok(arm_read_guard(con, ARMS["nomic_card"], texts) == 3, "EA-WRITE arm_read_guard admits 3/3 at 768-d")
                ok(_raises(lambda: arm_read_guard(con, ARMS["nomic_card"], texts + ["delta"]), "1 needed texts missing"),
                   "EA-WRITE arm_read_guard REFUSES a missing text")
                ok(_raises(lambda: arm_read_guard(con, ARMS["qwen3_raw"], texts), "!= {4096}"), "EA-WRITE arm_read_guard REFUSES a wrong dimension")
                ok(missing_texts(con, texts + ["delta", "eps"]) == ["delta", "eps"], "EA-WRITE missing_texts = the two absent texts")
            finally:
                con.close()
        if sel("EA-REFUSE"):
            ok(_raises(lambda: write_vectors(os.path.join(td, "embeddings_cache.db"), ARMS["gemma_raw"], texts, fake), "never writes the DB of record"),
               "EA-REFUSE the DB of record is never a target")
            q = os.path.join(td, "busy.db")
            open(q, "wb").close()
            with open(q + "-wal", "wb") as f:
                f.write(b"x")
            ok(_raises(lambda: write_vectors(q, ARMS["gemma_raw"], texts, fake), "non-empty"), "EA-REFUSE a target with a non-empty -wal")
            bad = lambda m, i: [[0.0] * 10 for _ in i]
            ok(_raises(lambda: write_vectors(os.path.join(td, "g.db"), ARMS["gemma_raw"], texts, bad), "returned a 10-d vector"),
               "EA-REFUSE a wrong-dimension response")
            ok(_raises(lambda: embed_missing("gemma_raw", 5, go=False, texts=texts, data_root=td, embed_fn=fake), "missing count"),
               "EA-REFUSE --expect-missing mismatch (3 missing, 5 expected)")
            before = len(posted)
            ok(embed_missing("gemma_raw", 3, go=False, texts=texts, data_root=td, embed_fn=fake) == 0 and len(posted) == before,
               "EA-REFUSE without --go nothing is posted or written")
        if sel("EA-CARD"):
            cd = os.path.join(td, "card")
            os.makedirs(cd)
            rawp = os.path.join(cd, cache_file(ARMS["nomic_raw"]))
            write_vectors(rawp, ARMS["nomic_raw"], texts, fake)
            before, raw_sha = len(posted), _sha(rawp)
            cardp = os.path.join(cd, cache_file(ARMS["nomic_card"]))
            ok(embed_card("nomic_card", False, data_root=cd, embed_fn=fake, texts=texts) == 0 and len(posted) == before
               and not os.path.exists(cardp) and _sha(rawp) == raw_sha and sorted(os.listdir(cd)) == [os.path.basename(rawp)],
               "EA-CARD embed_card(go=False): nothing posted, no card file created, the raw file unchanged (kills Y8-D)")
            ok(embed_card("nomic_card", True, data_root=cd, embed_fn=fake, texts=texts) == 3 and len(posted) == before + 1
               and os.path.exists(cardp), "EA-CARD embed_card(go=True): 3 vectors posted and written (the gate's other branch)")
        if sel("EA-PARITY"):
            pd = os.path.join(td, "parity")
            os.makedirs(pd)
            gp = os.path.join(pd, cache_file(ARMS["gemma_raw"]))
            ptexts = ["t%02d" % i for i in range(25)]
            rng = np.random.default_rng(7)
            base = {t: rng.normal(size=768) for t in ptexts}
            same = lambda m, i: [list(base[s]) for s in i]
            write_vectors(gp, ARMS["gemma_raw"], ptexts, same)
            ok(abs(route_parity(gp, ARMS["gemma_raw"], same) - 1.0) < 1e-6, "EA-PARITY identical route: min cos 1.000000 PASS")
            tail = lambda m, i: [list(base[s][:256]) + list(-3.0 * base[s][256:]) for s in i]
            ok(abs(route_parity(gp, ARMS["gemma_raw"], tail) - 1.0) < 1e-6,
               "EA-PARITY only dims beyond 256 differ: PASS (the comparison is slice-to-256, not full-dimension)")

            def tilt(v, c):
                # a 768-d vector whose first-256 slice has cos exactly c with v's slice; dims beyond 256 kept
                u = v[:256] / np.linalg.norm(v[:256])
                w = np.zeros(256)
                w[0], w[1] = u[1], -u[0]
                w = w - np.dot(w, u) * u
                w = w / np.linalg.norm(w)
                return list(np.linalg.norm(v[:256]) * (c * u + np.sqrt(1.0 - c * c) * w)) + list(v[256:])
            asked = []
            one_off = lambda m, i: (asked.append(len(i)), [tilt(base[s], 0.9995) if k == 0 else list(base[s])
                                                            for k, s in enumerate(i)])[1]
            ok(_raises(lambda: route_parity(gp, ARMS["gemma_raw"], one_off), "min cos 0.9995"),
               "EA-PARITY one of 20 texts at cos 0.9995 (mean 0.999975 and median 1 would pass): REFUSES on the MIN")
            ok(asked == [20], "EA-PARITY exactly 20 texts re-embedded (%s)" % asked)
            ok(abs(route_parity(gp, ARMS["gemma_raw"], lambda m, i: [tilt(base[s], 0.99995) for s in i]) - 0.99995) < 1e-6,
               "EA-PARITY every text at cos 0.99995 (>= 0.9999): PASS, min printed 0.999950")
            os.makedirs(os.path.join(pd, "few"))
            few = os.path.join(pd, "few", cache_file(ARMS["gemma_raw"]))
            write_vectors(few, ARMS["gemma_raw"], ptexts[:19], same)
            ok(_raises(lambda: route_parity(few, ARMS["gemma_raw"], same), "19 existing rows"), "EA-PARITY 19 rows < 20: REFUSES")
            ok(_raises(lambda: route_parity(os.path.join(pd, "absent.db"), ARMS["gemma_raw"], same), "absent"),
               "EA-PARITY absent target: REFUSES")
            miss_t = ptexts + ["new1", "new2"]
            base.update({t: rng.normal(size=768) for t in ("new1", "new2")})
            sha0 = _sha(gp)
            ok(_raises(lambda: embed_missing("gemma_raw", 2, go=True, texts=miss_t, data_root=pd, embed_fn=one_off), "min cos")
               and _sha(gp) == sha0, "EA-PARITY embed_missing --go with a failing parity REFUSES before any write (sha unchanged)")
            ok(embed_missing("gemma_raw", 2, go=True, texts=miss_t, data_root=pd, embed_fn=same) == 2,
               "EA-PARITY embed_missing --go with parity PASS writes the 2 missing vectors")
        if sel("EA-FMGUARD"):
            st_fmguard(ok, td)
        if sel("EA-TARGET"):
            st_target(ok, td)
        if sel("EA-TREADER"):
            st_treader(ok, td)
        if sel("EA-CONN"):
            st_conn(ok, td)
        if sel("EA-PACE"):
            st_pace(ok, td)
        if sel("EA-PINFILE"):
            with open(ARM_PINS_FILE, encoding="utf-8") as f:
                pj = json.load(f)
            arms4 = sorted(a for a in ARMS if a != "qwen3_raw")
            ok(pj.get("schema") == ARM_PINS_SCHEMA and sorted(pj["arms"]) == arms4
               and all(pj["arms"][a]["file"] == cache_file(ARMS[a]) for a in arms4)
               and all(v["sha256"] is None or (isinstance(v["sha256"], str) and len(v["sha256"]) == 64
                                               and all(c in "0123456789abcdef" for c in v["sha256"])) for v in pj["arms"].values()),
               "EA-PINFILE the committed registrar pin file: schema %s, the 4 non-qwen3 arms with their file names, each sha256 null "
               "(not yet bracketed: every read REFUSES) or 64 hex" % ARM_PINS_SCHEMA)
            nulls = [a for a in arms4 if pj["arms"][a]["sha256"] is None]
            ok(all(_raises(lambda a=a: registrar_pin(ARMS[a], "0" * 64), "no sha256 for arm %s yet" % a) for a in nulls),
               "EA-PINFILE every arm still null in the committed file REFUSES a read (%d null)" % len(nulls))
    return n[0]


def st_fmguard(ok, td):
    """RP08 delta (w0-delta3): the run of record imports flat_mix_mmlu (needed_texts) BEFORE its reads, so its connect guard is on
    sqlite3.connect. Stub DBs under td, the REAL guard installed; the pre-embedder's reads of the SELECTED arm's file pass, every
    other arm file stays refused, the admission does not outlive the open, and the guard's -wal rule still binds the admitted file."""
    import flat_mix_mmlu as FMm
    saved_connect, allowed0 = sqlite3.connect, FMm.ALLOWED_DB_BASENAMES
    gd = os.path.join(td, "fmguard")
    os.makedirs(gd)
    rng = np.random.default_rng(11)
    ftexts = ["f%02d" % i for i in range(22)]
    base = {t: rng.normal(size=768) for t in ftexts + ["m1", "m2"]}
    same = lambda m, i: [list(base[s[len("task: clustering | query: "):] if s.startswith("task: ") else s]) for s in i]
    gp, npth = os.path.join(gd, cache_file(ARMS["gemma_raw"])), os.path.join(gd, cache_file(ARMS["nomic_raw"]))
    write_vectors(gp, ARMS["gemma_raw"], ftexts, same)            # the writer bypasses the guard (sqlite3.connect._raw)
    write_vectors(npth, ARMS["nomic_raw"], ftexts[:3], same)
    sqlite3.connect = FMm._guarded_connect
    try:
        ok(_raises(lambda: pool_guard.open_ro(gp), "is not a DB this test reads"),
           "EA-FMGUARD the witness of main 481b613: a bare open_ro of the gemma arm file under the guard REFUSES")
        ok(embed_missing("gemma_raw", 2, go=False, texts=ftexts + ["m1", "m2"], data_root=gd, embed_fn=same) == 0,
           "EA-FMGUARD embed_missing gemma_raw (dry) reads the selected arm file under the guard: 2 missing, no refusal")
        ok(FMm.ALLOWED_DB_BASENAMES == allowed0, "EA-FMGUARD the admission does not outlive the open (guard tuple restored)")
        ok(_raises(lambda: pool_guard.open_ro(npth), "is not a DB this test reads"),
           "EA-FMGUARD a non-selected arm file (nomic raw) is still refused after the gemma reads")
        with _admit_arm_file(gp, ARMS["gemma_raw"]):
            inside = (FMm.ALLOWED_DB_BASENAMES == allowed0 + (cache_file(ARMS["gemma_raw"]),),
                      _raises(lambda: pool_guard.open_ro(npth), "is not a DB this test reads"))
        ok(inside == (True, True), "EA-FMGUARD DURING the gemma admission exactly one name is added and nomic raw is refused (%s)" % (inside,))
        ok(_raises(lambda: open_arm_ro(npth, ARMS["gemma_raw"]), "the arm's file is"),
           "EA-FMGUARD a path that is not the selected arm's file REFUSES by name")
        ok(embed_missing("gemma_raw", 2, go=True, texts=ftexts + ["m1", "m2"], data_root=gd, embed_fn=same) == 2
           and FMm.ALLOWED_DB_BASENAMES == allowed0,
           "EA-FMGUARD embed_missing gemma_raw --go under the guard: parity read + 2 vectors written; tuple restored")
        ok(embed_card("gemma_card", True, data_root=gd, embed_fn=same, texts=ftexts[:3]) == 3,
           "EA-FMGUARD embed_card gemma_card --go under the guard: the raw queries source is admitted, 3 written")
        with open(gp + "-wal", "wb") as f:
            f.write(b"x")
        ok(_raises(lambda: embed_missing("gemma_raw", 0, go=False, texts=ftexts, data_root=gd, embed_fn=same), "non-empty"),
           "EA-FMGUARD a non-empty -wal beside the admitted arm file still REFUSES (the guard's other rules bind)")
        os.remove(gp + "-wal")
    finally:
        sqlite3.connect = saved_connect
        FMm.ALLOWED_DB_BASENAMES = allowed0


def st_conn(ok, td):
    """EMB-CONN: one persistent connection; bounded whole-batch retry on transient connection errors only; I-2 host."""
    cases = {"0.0.0.0": "http://127.0.0.1:11434", "0.0.0.0:11500": "http://127.0.0.1:11500", "": "http://127.0.0.1:11434",
             ":11434": "http://127.0.0.1:11434", "127.0.0.1": "http://127.0.0.1:11434", "localhost:11434": "http://localhost:11434",
             "http://127.0.0.1:11434/": "http://127.0.0.1:11434", "http://0.0.0.0:11434": "http://127.0.0.1:11434",
             "[::]:11434": "http://127.0.0.1:11434", "https://ollama.local:8443": "https://ollama.local:8443"}
    got = {h: client_base(h) for h in cases}
    ok(got == cases, "EA-CONN I-2 client_base: bind forms (0.0.0.0, ::, :port) -> 127.0.0.1, bare host -> http://, port 11434 (%s)"
       % {h: g for h, g in got.items() if g != cases[h]})
    g = globals()
    saved = (g["OLLAMA_URL"], g["_sleep"])
    slept = []
    arm = ARMS["gemma_raw"]
    texts = ["c%03d" % i for i in range(100)]
    with stub_ollama() as (url, log, state):
        try:
            g["OLLAMA_URL"], g["_sleep"] = url, (lambda s: slept.append(s))
            p1 = os.path.join(td, "conn1.db")
            _capture(lambda: write_vectors(p1, arm, texts, ollama_embed))
            ok(len(log) == 4 and state["conns"] == 1 and slept == [],
               "EA-CONN 4 batches of <= %d over ONE connection (stub counted %d connection(s)), no retry" % (BATCH, state["conns"]))
            state["fault"] = lambda i: "port" if i in (5, 6) else None
            p2 = os.path.join(td, "conn2.db")
            out, err, n = _capture(lambda: write_vectors(p2, arm, texts, ollama_embed))
            rows = _rows_raw(p2)
            ok(err is None and n == 100 and len(rows) == 100 and slept == [2.0, 8.0] and len(log) == 4 + 6
               and log[5][2] == log[6][2] == log[7][2] == texts[32:64] and "retrying the WHOLE batch in 2 s (1 of 5)" in out,
               "EA-CONN incident W2's HTTP 400 'Only one usage of each socket address' twice on batch 2: the WHOLE batch retried "
               "after 2 s and 8 s, then written; 100 rows, no duplicate")
            del slept[:]
            state["fault"] = lambda i: "drop" if i == len(log) - 1 and not state.get("dropped") and not state.update(dropped=1) else None
            c0 = state["conns"]
            p3 = os.path.join(td, "conn3.db")
            out, err, n = _capture(lambda: write_vectors(p3, arm, texts, ollama_embed))
            ok(err is None and n == 100 and len(_rows_raw(p3)) == 100 and slept == [2.0] and state["conns"] == c0 + 1
               and client_for(url)[0].opened == state["conns"],
               "EA-CONN a connection dropped without a response: reset and reopened by the client (%d new; client opened %d = "
               "server saw %d), the batch retried whole, 100 rows" % (state["conns"] - c0, client_for(url)[0].opened, state["conns"]))
            del slept[:]
            nlog = len(log)
            state["fault"] = lambda i: "port" if i >= nlog + 2 else None      # batches 1-2 answered, batch 3 fails every time
            p4 = os.path.join(td, "conn4.db")
            out, err, n = _capture(lambda: write_vectors(p4, arm, texts, ollama_embed))
            ok(err is not None and "6 attempts of one batch" in err and slept == list(RETRY_BACKOFF_S) and len(_rows_raw(p4)) == 2 * BATCH, "EA-CONN a persistent transient error: 6 attempts, backoff %s, then REFUSED; the file holds "
               "%d rows = whole batches only" % (list(RETRY_BACKOFF_S), len(_rows_raw(p4))))
            for fault, needle, what in (("bad", "not a transient connection error: no retry", "a non-transient HTTP 400"),
                                        ("short", "Ollama returned 31 embeddings for 32 inputs", "a count mismatch")):
                del slept[:]
                state["fault"] = (lambda f_: (lambda i: f_))(fault)
                nlog = len(log)
                _o, err, _n = _capture(lambda: ollama_embed(arm.model, texts[:32]))
                ok(err is not None and needle in err and slept == [] and len(log) == nlog + 1,
                   "EA-CONN %s REFUSES on the first attempt: no retry, no sleep" % what)
            state["fault"] = None
            ok(_raises(lambda: write_vectors(os.path.join(td, "conn5.db"), arm, texts[:3], lambda m, i: [[0.0] * 10 for _ in i]),
                       "returned a 10-d vector") and slept == [], "EA-CONN a dimension mismatch REFUSES, never retried")
        finally:
            g["OLLAMA_URL"], g["_sleep"] = saved


def st_pace(ok, td):
    """EMB-PACE: (a) the WSAENOBUFS 400 is transient; (b) pacing off by default (no extra sleep, no probe), on with the flags."""
    g = globals()
    saved = (g["OLLAMA_URL"], g["_sleep"], g["_tw_count"], g["PACE_S"], g["TW_DRAIN"])
    slept, probes = [], []
    arm = ARMS["gemma_raw"]
    texts = ["p%03d" % i for i in range(100)]
    with stub_ollama() as (url, log, state):
        try:
            g["OLLAMA_URL"], g["_sleep"] = url, (lambda s: slept.append(s))
            seq = iter([5000, 3000, 100])
            g["_tw_count"] = lambda: (probes.append(1), next(seq, 100))[1]
            # (a) + no flag: the incident's body on batch 2 twice -> retried whole after 2 s and 8 s; no probe, no pause
            state["fault"] = lambda i: "nobufs" if i in (1, 2) else None
            out, err, n = _capture(lambda: write_vectors(os.path.join(td, "pace1.db"), arm, texts, ollama_embed))
            ok(err is None and n == 100 and len(_rows_raw(os.path.join(td, "pace1.db"))) == 100 and slept == [2.0, 8.0] and probes == []
               and log[1][2] == log[2][2] == log[3][2] == texts[32:64],
               "EA-PACE (a) the WSAENOBUFS 'lacked sufficient buffer space ... queue was full' 400 is retried whole (2 s, 8 s); "
               "no flag: 0 TIME_WAIT probes, no pause (sleeps %s)" % slept)
            del slept[:]
            state["fault"] = None
            _capture(lambda: write_vectors(os.path.join(td, "pace2.db"), arm, texts, ollama_embed))
            ok(slept == [] and probes == [], "EA-PACE no flag, no fault: no sleep at all, no probe (the pre-change behaviour)")
            g["PACE_S"] = 1.5
            _capture(lambda: write_vectors(os.path.join(td, "pace3.db"), arm, texts, ollama_embed))
            ok(slept == [1.5] * 4 and probes == [], "EA-PACE PACE_S 1.5: one pause after each of the 4 committed batches")
            g["PACE_S"], g["TW_DRAIN"] = 0.0, 2000
            del slept[:]
            state["fault"] = (lambda k0: (lambda i: "nobufs" if i == k0 + 1 else None))(len(log))
            out, err, n = _capture(lambda: write_vectors(os.path.join(td, "pace4.db"), arm, texts, ollama_embed))
            ok(err is None and n == 100 and slept == [2.0, TW_POLL_S, TW_POLL_S] and len(probes) == 3 and "TIME_WAIT 100 (threshold 2000) after 20 s" in out
               and "TIME_WAIT 3000" not in out, "EA-PACE TW_DRAIN 2000: after the 2 s backoff, TIME_WAIT polled (5000, 3000: wait %.0f s each; 100 < 2000) "
               "until below the threshold, then the whole batch retried (sleeps %s, %d probes)" % (TW_POLL_S, slept, len(probes)))
            del slept[:], probes[:]
            g["_tw_count"] = lambda: (probes.append(1), None)[1]
            state["fault"] = (lambda k0: (lambda i: "nobufs" if i == k0 + 1 else None))(len(log))
            out, err, n = _capture(lambda: write_vectors(os.path.join(td, "pace5.db"), arm, texts, ollama_embed))
            ok(err is None and slept == [2.0, TW_MAX_S] and "unreadable" in out, "EA-PACE an unreadable TIME_WAIT count waits TW_MAX_S once, printed")
            del slept[:], probes[:]
            g["_tw_count"] = lambda: (probes.append(1), 9999)[1]
            state["fault"] = (lambda k0: (lambda i: "nobufs" if i == k0 + 1 else None))(len(log))
            out, err, n = _capture(lambda: write_vectors(os.path.join(td, "pace6.db"), arm, texts, ollama_embed))
            ok(err is None and slept == [2.0] + [TW_POLL_S] * int(TW_MAX_S / TW_POLL_S) and "cap reached" in out,
               "EA-PACE a TIME_WAIT count that never drains: polled to the TW_MAX_S cap, then the batch retried (bounded)")
        finally:
            g["OLLAMA_URL"], g["_sleep"], g["_tw_count"], g["PACE_S"], g["TW_DRAIN"] = saved


def _rows_raw(path):
    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(path)
    try:
        return [t for (t,) in c.execute("SELECT query FROM embeddings")]
    finally:
        c.close()


def _stub_vec(text, dim, salt=""):
    seed = int(hashlib.sha256((salt + text).encode("utf-8")).hexdigest()[:8], 16)
    return [float(x) for x in np.random.default_rng(seed).normal(size=dim)]


@contextlib.contextmanager
def stub_ollama():
    """A STUB Ollama on 127.0.0.1 (ephemeral port; no real embedder is contacted): POST /api/embed -> deterministic vectors of the
    model's native dimension, seeded by sha256(state['salt'] + text); every request logged as (path, model, inputs)."""
    import threading
    import http.server
    log, state = [], {"salt": "", "conns": 0, "fault": None}

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"            # keep-alive (the client's persistent connection is observable: state['conns'])
        timeout = 10

        def setup(self):
            state["conns"] += 1
            http.server.BaseHTTPRequestHandler.setup(self)

        def do_GET(self):                        # /api/tags: a digest per model the stub serves
            body = json.dumps({"models": [{"name": m, "digest": "stubdigest-" + m} for m in sorted(EG.NATIVE_DIM, reverse=True)]}).encode("utf-8")
            self.send_response(200 if self.path == "/api/tags" else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode("utf-8"))
            log.append((self.path, req.get("model"), list(req.get("input") or [])))
            fault = state["fault"](len(log) - 1) if state["fault"] else None
            if fault == "drop":                  # the connection dies without a response (a transient connection error)
                self.close_connection = True
                self.wfile.flush()
                self.connection.shutdown(2)
                return
            dim = EG.NATIVE_DIM[EG.canonical_model(req["model"])]
            embs = [_stub_vec(s, dim, state["salt"]) for s in req["input"]]
            code = 200 if self.path == "/api/embed" else 404
            if fault == "port":                  # incident W2's server-side error, verbatim shape
                code, embs = 400, None
                body = json.dumps({"error": "Post \"http://127.0.0.1:51176/tokenize\": dial tcp 127.0.0.1:51176: connectex: Only "
                                            "one usage of each socket address (protocol/network address/port) is normally "
                                            "permitted."}).encode("utf-8")
            elif fault == "nobufs":              # the INTENT-TRANSFER-S0 qwen3 incident's body, verbatim shape (WSAENOBUFS)
                code, embs = 400, None
                body = json.dumps({"error": "Post \"http://127.0.0.1:49939/tokenize\": dial tcp 127.0.0.1:49939: bind: An operation on "
                                            "a socket could not be performed because the system lacked sufficient buffer space or "
                                            "because a queue was full."}).encode("utf-8")
            elif fault == "bad":
                code, body = 400, json.dumps({"error": "model is required"}).encode("utf-8")
            else:
                if fault == "short":
                    embs = embs[:-1]
                body = json.dumps({"model": req["model"], "embeddings": embs}).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    try:
        yield "http://127.0.0.1:%d/api/embed" % srv.server_address[1], log, state
    finally:
        close_clients()
        srv.shutdown()
        srv.server_close()


def _capture(fn):
    """-> (printed text, the refusal message or None, the return value or None). Only SystemExit is caught."""
    import io
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as e:
            err = str(e)
    return buf.getvalue(), err, res


def _rows(path, arm):
    con = open_arm_ro(path, arm)
    try:
        return {t: bytes(b) for t, b in con.execute("SELECT query, vector FROM embeddings")}
    finally:
        con.close()


def st_target(ok, td):
    """EMB-TARGET-DIR, the WRITER, end to end through main(argv) and a STUB Ollama over HTTP (ollama_embed's real route): the
    source under the data root is byte-unchanged, only DIR/<the arm's basename> (+ its provenance) is written, and every refusal
    (the source as a target, a second copy, the source's -wal, --expect-missing, parity, a corrupt copy, a source write) fires
    with nothing written. The pool guard and needed_texts are stubbed (synthetic; the pool is not read)."""
    g = globals()
    saved = (g["OLLAMA_URL"], g["needed_texts"], g["_copyfile"], pool_guard.DATA_ROOT, pool_guard.assert_pool_of_record)
    gr, gc = ARMS["gemma_raw"], ARMS["gemma_card"]
    root, gname = os.path.join(td, "tgt_root"), cache_file(gr)
    os.makedirs(root)
    src = os.path.join(root, gname)
    base_t = ["s%02d" % i for i in range(25)]
    texts = base_t + ["new1", "new2"]
    D = {k: os.path.join(td, "tgt_" + k) for k in ("dry", "go", "card", "carddry", "bad", "wal", "exp", "par", "chg")}
    for d in D.values():
        os.makedirs(d)
    argv = ["--embed-missing", "gemma_raw", "--expect-missing", "2", "--target-dir"]
    with stub_ollama() as (url, log, state):
        try:
            g["OLLAMA_URL"] = url
            g["needed_texts"] = lambda: list(texts)
            pool_guard.DATA_ROOT = root
            pool_guard.assert_pool_of_record = lambda pid, *a, **k: print("[POOL] %s (stub: selftest, synthetic)" % pid)
            _capture(lambda: write_vectors(src, gr, base_t, ollama_embed))      # the source: 25 rows via the stub route
            con = getattr(sqlite3.connect, "_raw", sqlite3.connect)(src)
            con.execute("INSERT INTO queries VALUES ('q1', 's00', 's00', 'cat', 7)")
            con.commit()
            con.close()
            sha0, rows0 = _sha(src), _rows(src, gr)
            ok(len(rows0) == 25 and log[-1][1:] == ("embeddinggemma:latest", base_t), "EA-TARGET the source: 25 rows posted through the stub Ollama")
            n0 = len(log)
            out, err, rc = _capture(lambda: main(argv + [D["dry"]]))
            ok(err is None and rc == 0 and "25 missing" not in out and ", 2 missing from %s" % src in out
               and ("source %s sha256 %s" % (src, sha0)) in out and os.listdir(D["dry"]) == [] and len(log) == n0 and _sha(src) == sha0,
               "EA-TARGET dry: 2 missing counted on the source, its sha256 printed, nothing posted, DIR empty, source unchanged")
            out, err, rc = _capture(lambda: main(argv + [D["go"], "--go"]))
            copy = os.path.join(os.path.abspath(D["go"]), gname)
            ok(err is None and rc == 0 and os.path.isfile(copy), "EA-TARGET --go: the copy written at DIR/%s (%s)" % (gname, err))
            ok(_sha(src) == sha0 and _rows(src, gr) == rows0, "EA-TARGET --go: the SOURCE is byte-unchanged (sha256 %s, 25 rows)" % sha0[:12])
            got = _rows(copy, gr)
            ok(sorted(got) == sorted(texts) and all(got[t] == rows0[t] for t in base_t),
               "EA-TARGET --go: the copy holds the source's 25 rows byte-for-byte + the 2 missing (27)")
            ok([(p, len(i)) for p, _m, i in log[n0:]] == [("/api/embed", 20), ("/api/embed", 2)] and log[-1][2] == ["new1", "new2"],
               "EA-TARGET --go: parity 20 texts then the 2 missing posted to the stub's /api/embed (%s)" % [len(i) for _p, _m, i in log[n0:]])
            with open(copy + PROVENANCE_SUFFIX, encoding="utf-8") as f:
                prov = json.load(f)
            sha_c = _sha(copy)
            ok(prov["source_sha256"] == sha0 and prov["sha256_after"] == sha_c and prov["vectors_written"] == 2 and prov["arm"] == "gemma_raw"
               and _norm(prov["source"]) == _norm(src) and prov["copy_basename"] == gname and _norm(prov["copy"]) == _norm(copy),
               "EA-TARGET provenance: arm, source + its sha256, copy + its sha256 after, 2 vectors")
            ok(prov["model_digest"] == "stubdigest-embeddinggemma:latest" and "model digest stubdigest-embeddinggemma:latest" in out,
               "EA-TARGET C-E0B-7 the provenance records the model's tag digest at the --go (%s)" % prov.get("model_digest"))
            ok(("target %s (exists) sha256 before %s" % (copy, sha0)) in out and ("wrote 2 vectors; sha256 after %s" % sha_c) in out
               and ("sha256 %s (copy == source, verified)" % sha0) in out, "EA-TARGET the sha256 before (the copy's = the source's) and after printed")
            ok(sorted(os.listdir(D["go"])) == sorted([gname, gname + PROVENANCE_SUFFIX]) and os.listdir(root) == [gname],
               "EA-TARGET only the copy and its provenance in DIR; nothing new beside the source")
            n1 = len(log)
            for d, needle, what in ((D["go"], "is written once", "a second run into the same DIR (copy exists)"),
                                    (root, "the source is never a target", "DIR = the source's directory"),
                                    (os.path.join(root, "..", "tgt_root") + os.sep, "the source is never a target",
                                     "DIR = the source's directory, spelled ../tgt_root/"),
                                    (os.path.join(td, "absent_dir"), "not an existing directory", "an absent DIR")):
                out, err, rc = _capture(lambda: main(argv + [d, "--go"]))
                ok(err is not None and needle in err and _sha(src) == sha0 and _sha(copy) == sha_c and len(log) == n1,
                   "EA-TARGET REFUSES %s ('%s'); nothing posted, source and copy unchanged" % (what, needle))
            out, err, rc = _capture(lambda: main(["--plan", "--target-dir", D["bad"]]))
            ok(err is not None and "--target-dir is admitted with --embed-missing / --embed-card only" in err, "EA-TARGET --target-dir with --plan REFUSES")
            out, err, rc = _capture(lambda: main(["--embed-missing", "gemma_raw", "--expect-missing", "5", "--target-dir", D["exp"], "--go"]))
            ok(err is not None and "missing count 2 != --expect-missing 5" in err and os.listdir(D["exp"]) == [] and len(log) == n1,
               "EA-TARGET --expect-missing 5 (2 missing) REFUSES under --target-dir: DIR empty, nothing posted")
            ok(_raises(lambda: embed_missing("qwen3_raw", 0, True, texts=texts, data_root=root, target_dir=D["bad"]), "non-qwen3 RAW arms")
               and os.listdir(D["bad"]) == [], "EA-TARGET qwen3_raw REFUSED by name under --target-dir")
            with open(src + "-wal", "wb") as f:
                f.write(b"x")
            out, err, rc = _capture(lambda: main(argv + [D["wal"], "--go"]))
            os.remove(src + "-wal")
            ok(err is not None and "checkpoints the source before it is copied" in err and os.listdir(D["wal"]) == [] and len(log) == n1,
               "EA-TARGET a non-empty -wal beside the SOURCE REFUSES before any copy")
            state["salt"] = "another route"
            out, err, rc = _capture(lambda: main(argv + [D["par"], "--go"]))
            state["salt"] = ""
            ok(err is not None and "route parity gemma_raw: min cos" in err and os.listdir(D["par"]) == [] and _sha(src) == sha0
               and len(log) == n1 + 1, "EA-TARGET a failing route parity REFUSES before the copy: DIR empty, source unchanged")
            n2 = len(log)
            g["_copyfile"] = lambda a, b: (shutil.copyfile(a, b), open(b, "ab").write(b"\0"))
            out, err, rc = _capture(lambda: main(argv + [D["bad"], "--go"]))
            g["_copyfile"] = saved[2]
            ok(err is not None and "!= source sha256" in err and not os.path.exists(os.path.join(D["bad"], gname + PROVENANCE_SUFFIX))
               and len(log) == n2 + 1 and _sha(src) == sha0, "EA-TARGET a copy whose sha256 differs from the source REFUSES before any write")
            out, err, rc = _capture(lambda: main(["--embed-card", "gemma_card", "--target-dir", D["carddry"]]))
            ok(err is None and os.listdir(D["carddry"]) == [] and len(log) == n2 + 1, "EA-TARGET card dry: DIR empty, nothing posted")
            out, err, rc = _capture(lambda: main(["--embed-card", "gemma_card", "--target-dir", D["card"], "--go"]))
            card = os.path.join(os.path.abspath(D["card"]), cache_file(gc))
            ok(err is None and sorted(os.listdir(D["card"])) == sorted([cache_file(gc), cache_file(gc) + PROVENANCE_SUFFIX])
               and os.listdir(root) == [gname] and _sha(src) == sha0, "EA-TARGET card --go: a NEW card file in DIR; none beside the source; source unchanged (%s)" % err)
            ok(sorted(_rows(card, gc)) == sorted(texts) and log[-1][2] == [gc.prefix + t for t in texts],
               "EA-TARGET card --go: 27 texts posted with the card prefix, stored under the raw text")
            cq = open_arm_ro(card, gc)
            try:
                qrows = cq.execute("SELECT id, raw_text, query_id FROM queries").fetchall()
            finally:
                cq.close()
            with open(card + PROVENANCE_SUFFIX, encoding="utf-8") as f:
                cprov = json.load(f)
            ok(qrows == [("q1", "s00", 7)] and cprov["source_sha256"] == sha0 and cprov["arm"] == "gemma_card"
               and cprov["sha256_after"] == _sha(card), "EA-TARGET card provenance: the raw source's sha256; its queries rows copied")
            # C-ET-1: a file PLANTED at the copy path after target_paths' check (during the parity; for a card, after the check,
            # before any post) is never overwritten: the exclusive create REFUSES, the planted bytes survive, nothing more is posted
            for k in ("race", "racecard"):
                os.makedirs(os.path.join(td, "tgt_" + k))
            planted = os.path.join(td, "tgt_race", gname)

            def plant_during_parity(model, inputs):
                if not os.path.exists(planted):
                    with open(planted, "wb") as f:
                        f.write(b"PLANTED")
                return ollama_embed(model, inputs)
            nr = len(log)
            ok(_raises(lambda: embed_missing("gemma_raw", 2, True, texts=texts, data_root=root, embed_fn=plant_during_parity,
                                             target_dir=os.path.join(td, "tgt_race")), "appeared after the --target-dir check")
               and open(planted, "rb").read() == b"PLANTED" and len(log) == nr + 1 and _sha(src) == sha0
               and os.listdir(os.path.join(td, "tgt_race")) == [gname],
               "EA-TARGET C-ET-1 raw: a file planted during parity REFUSES the copy; planted bytes intact; parity only posted")
            planted_c = os.path.join(td, "tgt_racecard", cache_file(gc))

            def plant_then_texts():
                with open(planted_c, "wb") as f:
                    f.write(b"PLANTED")
                return list(texts)
            g["needed_texts"] = plant_then_texts
            nr = len(log)
            out, err, rc = _capture(lambda: main(["--embed-card", "gemma_card", "--target-dir", os.path.join(td, "tgt_racecard"), "--go"]))
            g["needed_texts"] = lambda: list(texts)
            ok(err is not None and "appeared after the --target-dir check" in err and open(planted_c, "rb").read() == b"PLANTED"
               and len(log) == nr and os.listdir(os.path.join(td, "tgt_racecard")) == [cache_file(gc)],
               "EA-TARGET C-ET-1 card: a file planted after the check REFUSES before any post; planted bytes intact (%s)" % err)
            calls = [0]

            def touch_src(model, inputs):
                calls[0] += 1
                if calls[0] == 2:                       # during the WRITE (call 1 is the parity): a write reaches the source
                    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(src)
                    c.execute("INSERT INTO queries VALUES ('q2', 'x', 'x', '', -1)")
                    c.commit()
                    c.close()
                return ollama_embed(model, inputs)
            ok(_raises(lambda: embed_missing("gemma_raw", 2, True, texts=texts, data_root=root, embed_fn=touch_src, target_dir=D["chg"]),
                       "changed during the run") and not os.path.exists(os.path.join(D["chg"], gname + PROVENANCE_SUFFIX)),
               "EA-TARGET a source modified during the run REFUSES the provenance (the source is never written by the run)")
        finally:
            g["OLLAMA_URL"], g["needed_texts"], g["_copyfile"], pool_guard.DATA_ROOT, pool_guard.assert_pool_of_record = saved


def st_treader(ok, td):
    """EMB-TARGET-DIR, the READER (EMBEDDER-CROSS-FLAT's: configure_arm -> flat_mix_mmlu.configure_embedding, the embedder guard
    embedding_guard_flat, the flat_mix connect guard): a --target-dir copy made UNDER the real connect guard is read, and only it:
    the source (same basename, under the data root; 118 of 120 texts) is refused by path; a moved or modified copy, the source
    directory, qwen3 and an arm with no copy all REFUSE. Every flat_mix global and sqlite3.connect restored."""
    import flat_mix_mmlu as FMm
    saved_connect = sqlite3.connect
    saved_g = {k: getattr(FMm, k) for k in FMm._EMB_GLOBALS}
    saved_af, saved_f = FMm.AF.EMB_DB, FMm.F.EMB_DB
    vec, byid, ids = EG.synthetic(np.random.default_rng(31))
    v768 = {"text " + q: np.asarray(v[:768]) for q, v in vec.items()}
    rd, cd, cd2 = os.path.join(td, "tr_root"), os.path.join(td, "tr_copy"), os.path.join(td, "tr_moved")
    for d in (rd, cd, cd2):
        os.makedirs(d)
    gr, gname = ARMS["gemma_raw"], cache_file(ARMS["gemma_raw"])
    src = EG._make_cache(os.path.join(rd, gname), {q: v[:768] for q, v in vec.items()})
    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(src)
    c.execute("DELETE FROM embeddings WHERE query IN ('text q_a00', 'text q_b00')")     # queries rows kept: 2 vectors missing
    c.commit()
    c.close()
    mq = os.path.join(td, "tr_manifest.json")
    with open(mq, "w", encoding="utf-8") as f:
        json.dump({"embedding_model": "embeddinggemma:latest"}, f)
    graph = dict(byid=byid, root="n1", sha="synthetic")
    copy = os.path.join(os.path.abspath(cd), gname)

    g = globals()
    saved_pf = g["ARM_PINS_FILE"]
    pf = os.path.join(td, "tr_pins.json")                  # the TEST FIXTURE of the registrar's pin file (C-ET-4)

    def restore():
        sqlite3.connect = saved_connect
        for k, v in saved_g.items():
            setattr(FMm, k, v)
        FMm.AF.EMB_DB, FMm.F.EMB_DB = saved_af, saved_f
        g["ARM_PINS_FILE"] = saved_pf

    def pins(**arms):
        with open(pf, "w", encoding="utf-8") as f:
            json.dump({"schema": ARM_PINS_SCHEMA, "arms": {a: {"sha256": s} for a, s in arms.items()}}, f)
    try:
        sqlite3.connect = FMm._guarded_connect          # the run of record's state: the FLAT reader's connect guard is on
        n = _capture(lambda: embed_missing("gemma_raw", 2, True, texts=sorted(v768), data_root=rd,
                                           embed_fn=lambda m, i: [list(v768[s]) for s in i], target_dir=cd))
        ok(n[1] is None and n[2] == 2 and FMm.ALLOWED_DB_BASENAMES == saved_g["ALLOWED_DB_BASENAMES"],
           "EA-TREADER the copy made under the real connect guard: 2 written; the guard's tuple restored (%s)" % n[1])
        ok(_raises(lambda: pool_guard.open_ro(copy), "is not a DB this test reads"),
           "EA-TREADER before configure_arm the connect guard admits no arm file (the copy included)")
        # C-ET-3: the flat_mix --embedding-cache-file route cannot read the DIR copy (no provenance / pin check on that route)
        ok(_raises(lambda: FMm.configure_embedding(cache_file=copy, model="embeddinggemma:latest"), "is an EMBEDDER-CROSS-FLAT arm file")
           and FMm.EMB_DB_NAME == saved_g["EMB_DB_NAME"], "EA-TREADER C-ET-3 flat_mix.configure_embedding(<DIR copy>) REFUSES")
        saved_apr = pool_guard.assert_pool_of_record
        pool_guard.assert_pool_of_record = lambda *a, **k: refuse("selftest: the pool is not read")
        try:
            ok(_raises(lambda: FMm.main(["--dry-run", "--embedding-cache-file", copy, "--embedding-model", "embeddinggemma:latest"]),
                       "is an EMBEDDER-CROSS-FLAT arm file"), "EA-TREADER C-ET-3 flat_mix --dry-run --embedding-cache-file <DIR copy> REFUSES")
        finally:
            pool_guard.assert_pool_of_record = saved_apr
        ok(_raises(lambda: open_arm_reader(FMm, "gemma_raw", None, data_root=rd), "no DIR given") and FMm.EMB_DB_NAME == saved_g["EMB_DB_NAME"],
           "EA-TREADER C-ET-3 open_arm_reader(gemma_raw) without a DIR REFUSES (no root read)")
        # C-ET-4: the registrar's pin file, absent / not yet bracketed / wrong schema / a different sha256 -> REFUSED
        g["ARM_PINS_FILE"] = pf
        sha_c = _sha(copy)
        with open(pf, "w", encoding="utf-8") as f:
            json.dump({"schema": "other", "arms": {"gemma_raw": {"sha256": sha_c}}}, f)
        ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd), "expected %r" % ARM_PINS_SCHEMA), "EA-TREADER C-ET-4 a pin file of another schema REFUSES")
        pins(gemma_raw=None, gemma_card=sha_c)
        ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd), "no sha256 for arm gemma_raw yet"),
           "EA-TREADER C-ET-4 an arm not yet bracketed (sha256 null) REFUSES, even when another arm's pin matches")
        pins(gemma_raw="0" * 64)
        ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd), "!= the registrar's pin"), "EA-TREADER C-ET-4 a pin mismatch REFUSES")
        os.remove(pf)
        ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd), "pin file") and FMm.EMB_DB_NAME == saved_g["EMB_DB_NAME"],
           "EA-TREADER C-ET-4 the pin file absent REFUSES; nothing configured by any pin refusal")
        pins(gemma_raw=sha_c)
        out, err, p = _capture(lambda: open_arm_reader(FMm, "gemma_raw", cd, data_root=rd))
        ok(err is None and ("registrar pin: arm gemma_raw sha256 %s" % sha_c) in out and FMm.ARM_COPY_ADMITTED is None,
           "EA-TREADER C-ET-3/4 open_arm_reader(gemma_raw, DIR): the registrar pin printed; the flat_mix admission token cleared (%s)" % err)
        ok(err is None and p == copy and FMm.EMB_DB_NAME == os.path.abspath(copy) == FMm.AF.EMB_DB == FMm.F.EMB_DB
           and FMm.EMB_CACHE_SET is True and FMm.EMB_MODEL_EXPLICIT == "embeddinggemma:latest" and gname in FMm.ALLOWED_DB_BASENAMES,
           "EA-TREADER configure_arm(--target-dir): the FLAT reader's cache, AF, F, the model and the guard's admission are the copy's (%s)" % err)
        out, err, r = _capture(lambda: FMm.embedding_guard_flat(graph=graph, manifest_path=mq, dim=256))
        ok(err is None and bool(r["admitted"]) and [(x["id"], x["n"], x["found"]) for x in r["rows"]] == [("n1", 120, 120)]
           and ("cache=%s" % os.path.abspath(copy)) in out,
           "EA-TREADER the embedder guard reads the COPY and ADMITS it: 120 of 120 vectors (the source holds 118) (%s)" % err)
        ok(_raises(lambda: pool_guard.open_ro(src).close(), "only the copy"),
           "EA-TREADER the source (the same basename under the data root) is REFUSED by the path pin")
        con = pool_guard.open_ro(copy)
        try:
            ok(con.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0] == 120, "EA-TREADER the copy opens under the guard + pin: 120 rows")
        finally:
            con.close()
    finally:
        restore()
    ok(sqlite3.connect is saved_connect and FMm.EMB_DB_NAME == saved_g["EMB_DB_NAME"], "EA-TREADER sqlite3.connect and flat_mix's globals restored")
    try:
        st_treader_refusals(ok, FMm, saved_g, saved_connect, gr, gname, rd, cd, cd2, copy)
    finally:
        restore()                                     # a mutant that lets a refusal through leaves nothing configured behind


def st_treader_refusals(ok, FMm, saved_g, saved_connect, gr, gname, rd, cd, cd2, copy):
    unchanged = lambda: FMm.EMB_DB_NAME == saved_g["EMB_DB_NAME"] and sqlite3.connect is saved_connect
    for fn, needle, what in ((lambda: configure_arm(FMm, gr, rd, target_dir=rd), "source directory", "DIR = the source's directory"),
                             (lambda: configure_arm(FMm, ARMS["qwen3_raw"], rd, target_dir=cd), "DB of record", "qwen3_raw"),
                             (lambda: configure_arm(FMm, ARMS["gemma_card"], rd, target_dir=cd), "no --target-dir copy of arm gemma_card",
                              "an arm with no copy in DIR (gemma_card)")):
        ok(_raises(fn, needle) and unchanged(), "EA-TREADER REFUSES %s ('%s'); nothing configured" % (what, needle))
    for f in (gname, gname + PROVENANCE_SUFFIX):
        shutil.copyfile(os.path.join(cd, f), os.path.join(cd2, f))
    ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd2), "names arm") and unchanged(),
       "EA-TREADER a copy MOVED to another DIR (its provenance names the original path) REFUSES")
    c = getattr(sqlite3.connect, "_raw", sqlite3.connect)(copy)
    c.execute("INSERT INTO embeddings VALUES ('zz', ?)", (struct.pack(">768f", *([0.1] * 768)),))
    c.commit()
    c.close()
    ok(_raises(lambda: configure_arm(FMm, gr, rd, target_dir=cd), "modified after the pre-embedder wrote it") and unchanged(),
       "EA-TREADER a copy modified after its provenance REFUSES (sha256 != sha256_after)")


def _raises(fn, needle):
    try:
        fn()
    except SystemExit as e:
        return needle in str(e)
    return False


def embed_missing(arm_name, expect, go, texts=None, data_root=None, embed_fn=ollama_embed, target_dir=None):
    arm = ARMS[arm_name]
    if is_card(arm) or arm.name == "qwen3_raw":
        refuse("--embed-missing is for the non-qwen3 RAW arms (got %s)" % arm_name)
    root = data_root if data_root is not None else pool_guard.DATA_ROOT
    path = os.path.join(root, cache_file(arm))
    staged = resolve_target(arm, root, target_dir)
    texts = needed_texts() if texts is None else texts
    if os.path.exists(path):
        con = open_arm_ro(path, arm)
        try:
            miss = missing_texts(con, texts)
        finally:
            con.close()
    else:
        miss = sorted(set(texts))
    print("%s arm %s: %d needed texts, %d missing from %s (expected %s)" % (TAG, arm_name, len(set(texts)), len(miss), path, expect))
    if expect is None or len(miss) != int(expect):
        refuse("missing count %d != --expect-missing %s" % (len(miss), expect))
    if not go:
        print("%s dry: nothing posted, nothing written (add --go)" % TAG)
        return 0
    route_parity(path, arm, embed_fn)
    if staged is None:
        return write_vectors(path, arm, miss, embed_fn)
    source_sha = stage_copy(*staged)
    n = write_vectors(staged[1], arm, miss, embed_fn)
    write_provenance(staged[1], arm, staged[0], source_sha, n)
    return n


def embed_card(arm_name, go, data_root=None, embed_fn=ollama_embed, texts=None, target_dir=None):
    arm = ARMS[arm_name]
    if not is_card(arm):
        refuse("--embed-card is for the SECONDARY card arms (got %s)" % arm_name)
    root = data_root if data_root is not None else pool_guard.DATA_ROOT
    path = os.path.join(root, cache_file(arm))
    raw = os.path.join(root, EG.cache_file_for(arm.model))
    staged = resolve_target(arm, root, target_dir)
    if staged is not None:
        path = staged[1]
    texts = needed_texts() if texts is None else texts
    print("%s arm %s: %d needed texts -> %s (queries rows copied from %s)" % (TAG, arm_name, len(texts), path, raw))
    if not go:
        print("%s dry: nothing posted, nothing written (add --go)" % TAG)
        return 0
    if staged is None:
        return write_vectors(path, arm, texts, embed_fn, queries_src=raw)
    source_sha = _sha(raw)
    try:
        open(path, "xb").close()                        # C-ET-1: the NEW card file is created exclusively, before any post
    except FileExistsError:
        refuse("%s appeared after the --target-dir check: the exclusive create refused it; that file is left untouched (C-ET-1)" % path)
    n = write_vectors(path, arm, texts, embed_fn, queries_src=raw)
    write_provenance(path, arm, raw, source_sha, n)
    return n


def plan():
    texts = needed_texts()
    print("%s needed texts (fit 8,125 + held-out + keyed, distinct): %d" % (TAG, len(texts)))
    for a in ARMS.values():
        p = os.path.join(pool_guard.DATA_ROOT, cache_file(a))
        if not os.path.exists(p):
            print("%s arm %-10s %-9s %s: ABSENT" % (TAG, a.name, a.role, p))
            continue
        con = open_arm_ro(p, a)
        try:
            print("%s arm %-10s %-9s %s: %d missing" % (TAG, a.name, a.role, p, len(missing_texts(con, texts))))
        finally:
            con.close()
    return 0


def check_target_flag(a):
    """main(): --target-dir is admitted with --embed-missing / --embed-card only (above MUTANTS so the mutants reach it)."""
    if a.target_dir is not None and not (a.embed_missing or a.embed_card):
        refuse("--target-dir is admitted with --embed-missing / --embed-card only")


def run_embed(a):
    """main()'s --embed-* dispatch; --target-dir passed through (None when the flag is absent: the pre-existing calls)."""
    if a.embed_missing:
        embed_missing(a.embed_missing, a.expect_missing, a.go, target_dir=a.target_dir)
        return 0
    embed_card(a.embed_card, a.go, target_dir=a.target_dir)
    return 0


MUTANTS = (
    ("layer_norm dropped", "    if arm.layer_norm:\n        return", "    if False:\n        return", ("EA-LN", "EA-WRITE")),
    ("prefix not posted", "embed_fn(arm.model, [arm.prefix + t for t in ch])", "embed_fn(arm.model, list(ch))", ("EA-WRITE",)),
    ("stored under the prefixed text", "(t, struct.pack(\">%df\" % len(v), *v))", "(arm.prefix + t, struct.pack(\">%df\" % len(v), *v))", ("EA-WRITE",)),
    ("DB of record admitted as a target", "    if os.path.basename(path) == EG.DB_OF_RECORD:\n", "    if False:\n", ("EA-REFUSE",)),
    ("-wal ignored", "        if os.path.exists(sp) and os.path.getsize(sp) > 0:\n", "        if False:\n", ("EA-REFUSE",)),
    ("dimension of the response unchecked", "                if len(e) != native:\n", "                if False:\n", ("EA-REFUSE",)),
    ("expect-missing unchecked", "    if expect is None or len(miss) != int(expect):\n", "    if False:\n", ("EA-REFUSE",)),
    ("--go ignored", "    if not go:\n        print(\"%s dry: nothing posted, nothing written (add --go)\" % TAG)\n        return 0\n    route_parity(path, arm, embed_fn)\n    if staged is None:",
     "    route_parity(path, arm, embed_fn)\n    if staged is None:", ("EA-REFUSE",)),
    ("qwen3 given a flag", "    if arm.name == \"qwen3_raw\":\n        return None\n", "", ("EA-WIRE",)),
    ("model not named", "    FM.configure_embedding(cache_file=path, model=arm.model)", "    FM.configure_embedding(cache_file=path, model=None)", ("EA-WIRE",)),
    ("read guard ignores dims", "    if missing or set(dims) - {native}:\n", "    if missing:\n", ("EA-WRITE",)),
    ("embed_card ignores --go (Y8-D)", "    if not go:\n        print(\"%s dry: nothing posted, nothing written (add --go)\" % TAG)\n        return 0\n    if staged is None:\n        return write_vectors(path, arm, texts",
     "    if staged is None:\n        return write_vectors(path, arm, texts", ("EA-CARD",)),
    ("parity not called under --go", "    route_parity(path, arm, embed_fn)\n", "", ("EA-PARITY",)),
    ("parity bar on the mean", "    mn = min(cos)\n", "    mn = float(np.mean(cos))\n", ("EA-PARITY",)),
    ("parity bar on the median", "    mn = min(cos)\n", "    mn = float(np.median(cos))\n", ("EA-PARITY",)),
    ("parity bar on the max", "    mn = min(cos)\n", "    mn = max(cos)\n", ("EA-PARITY",)),
    ("parity full dimension, no slice", "    v = np.asarray(v, dtype=np.float64)[:d]\n", "    v = np.asarray(v, dtype=np.float64)\n", ("EA-PARITY",)),
    ("parity bar 0.999", "PARITY_COS = 0.9999\n", "PARITY_COS = 0.999\n", ("EA-PARITY",)),
    ("parity n = 19", "PARITY_N = 20\n", "PARITY_N = 19\n", ("EA-PARITY",)),
    ("parity refuses nothing", "    if not mn >= bar:\n", "    if False:\n", ("EA-PARITY",)),
    ("parity row floor dropped", "    if len(rows) < n:\n", "    if False:\n", ("EA-PARITY",)),
    ("arm file admitted by no one (main 481b613)", "        fm.ALLOWED_DB_BASENAMES = saved + (base,)\n", "        pass\n", ("EA-FMGUARD",)),
    ("admission outlives the open", "        if fm is not None:\n            fm.ALLOWED_DB_BASENAMES = saved\n", "        pass\n", ("EA-FMGUARD",)),
    ("every arm file admitted", "        fm.ALLOWED_DB_BASENAMES = saved + (base,)\n",
     "        fm.ALLOWED_DB_BASENAMES = saved + tuple(cache_file(a) for a in ARMS.values())\n", ("EA-FMGUARD",)),
    ("arm-name check dropped", "    if base != cache_file(arm):\n", "    if False:\n", ("EA-FMGUARD",)),
    ("card source opened unadmitted", "            src = open_arm_ro(queries_src, raw_arm_of(arm))\n", "            src = pool_guard.open_ro(queries_src)\n", ("EA-FMGUARD",)),
    ("E0B7 digest not recorded", "               model_digest=model_digest(arm.model) or \"UNAVAILABLE\")", "               model_digest=\"UNAVAILABLE\")",
     ("EA-TARGET",)),
    ("E0B7 digest of another model", "        if model in (m.get(\"name\"), m.get(\"model\")):\n", "        if True:\n", ("EA-TARGET",)),
    ("CONN new connection per request", "        if r.will_close:\n            self.reset()\n", "        self.reset()\n", ("EA-CONN",)),
    ("CONN no retry on a transient error", "RETRY_BACKOFF_S = (2.0, 8.0, 30.0, 60.0, 120.0)", "RETRY_BACKOFF_S = ()", ("EA-CONN",)),
    ("CONN transient 400 treated as fatal", "    return status in (400, 500, 502, 503) and any(", "    return False and any(", ("EA-CONN",)),
    ("PACE WSAENOBUFS fatal", "                  \"lacked sufficient buffer space\", \"queue was full\", \"WSAENOBUFS\", \"10055\")",
     "                  )", ("EA-PACE",)),
    ("PACE pause ignored", "            if PACE_S > 0:\n                _sleep(PACE_S)\n", "", ("EA-PACE",)),
    ("PACE pause without the flag", "            if PACE_S > 0:\n                _sleep(PACE_S)\n", "            _sleep(PACE_S)\n", ("EA-PACE",)),
    ("PACE drain ignored", "        if TW_DRAIN is not None:\n            drain_time_wait(TW_DRAIN)\n", "", ("EA-PACE",)),
    ("PACE drain without the flag", "        if TW_DRAIN is not None:\n            drain_time_wait(TW_DRAIN)\n", "        drain_time_wait(TW_DRAIN or 0)\n", ("EA-PACE",)),
    ("PACE drain uncapped", "        if n < threshold or waited >= TW_MAX_S:\n", "        if n < threshold:\n", ("EA-PACE",)),
    ("PACE drain stops at <=", "        if n < threshold or waited >= TW_MAX_S:\n", "        if n <= threshold * 2 or waited >= TW_MAX_S:\n", ("EA-PACE",)),
    ("CONN any HTTP error retried", "    return status in (400, 500, 502, 503) and any(t.lower() in text.lower() for t in TRANSIENT_BODY)",
     "    return True", ("EA-CONN",)),
    ("CONN count mismatch retried", "    embs = out.get(\"embeddings\")\n    if not isinstance(embs, list) or len(embs) != len(inputs):\n",
     "    embs = out.get(\"embeddings\")\n    if not isinstance(embs, list) or len(embs) != len(inputs) and False:\n", ("EA-CONN",)),
    ("CONN backoff not applied", "        _sleep(RETRY_BACKOFF_S[attempt])\n", "        pass\n", ("EA-CONN",)),
    ("CONN dropped connection not reset", "        except (OSError, http.client.HTTPException) as e:        # ConnectionError, TimeoutError, WinError 10048, RemoteDisconnected\n            client.reset()\n",
     "        except (OSError, http.client.HTTPException) as e:        # ConnectionError, TimeoutError, WinError 10048, RemoteDisconnected\n            pass\n", ("EA-CONN",)),
    ("CONN 0.0.0.0 kept as the client host", "    if name in (\"\", \"0.0.0.0\", \"::\"):\n", "    if name in (\"\",):\n", ("EA-CONN",)),
    ("card file named as raw", "    return base[:-3] + \"__card.db\" if arm.role == \"SECONDARY\" else base\n", "    return base\n", ("EA-ARMS",)),
    # EMB-TARGET-DIR (2026-09-29): the writer (EA-TARGET, main(argv) + the stub Ollama) and the reader (EA-TREADER, the real guard)
    ("TD --target-dir WRITES TO THE SOURCE (raw)", "    n = write_vectors(staged[1], arm, miss, embed_fn)\n", "    n = write_vectors(path, arm, miss, embed_fn)\n", ("EA-TARGET",)),
    ("TD card written beside the source", "    if staged is not None:\n        path = staged[1]\n", "", ("EA-TARGET",)),
    ("TD main drops --target-dir (raw)", "        embed_missing(a.embed_missing, a.expect_missing, a.go, target_dir=a.target_dir)\n",
     "        embed_missing(a.embed_missing, a.expect_missing, a.go)\n", ("EA-TARGET",)),
    ("TD main drops --target-dir (card)", "    embed_card(a.embed_card, a.go, target_dir=a.target_dir)\n", "    embed_card(a.embed_card, a.go)\n", ("EA-TARGET",)),
    ("TD source directory admitted as a target", "    if _norm(target_dir) == _norm(root):\n", "    if False:\n", ("EA-TARGET",)),
    ("TD source dir compared unnormalised", "    if _norm(target_dir) == _norm(root):\n", "    if target_dir == root:\n", ("EA-TARGET",)),
    ("TD existing copy overwritten", "        if os.path.lexists(q):\n", "        if False:\n", ("EA-TARGET",)),
    ("TD source -wal not checked", "        if os.path.isfile(sp) and os.path.getsize(sp) > 0:\n", "        if False:\n", ("EA-TARGET",)),
    ("TD copy not verified", "    if not (sha_copy == sha_src == sha_src2):\n", "    if False:\n", ("EA-TARGET",)),
    ("TD dry run copies", "\"NEW card file\", copy))\n    return source, copy\n", "\"NEW card file\", copy))\n    _copyfile(source, copy)\n    return source, copy\n", ("EA-TARGET",)),
    ("TD --go ignored under --target-dir", "    if not go:\n        print(\"%s dry: nothing posted, nothing written (add --go)\" % TAG)\n        return 0\n    route_parity(path, arm, embed_fn)\n    if staged is None:",
     "    route_parity(path, arm, embed_fn)\n    if staged is None:", ("EA-TARGET",)),
    ("TD parity skipped under --target-dir", "    route_parity(path, arm, embed_fn)\n", "", ("EA-TARGET",)),
    ("TD provenance source sha taken from the copy", "    write_provenance(staged[1], arm, staged[0], source_sha, n)\n",
     "    write_provenance(staged[1], arm, staged[0], _sha(staged[1]), n)\n", ("EA-TARGET",)),
    ("TD source change unchecked", "    if now != source_sha:\n", "    if False:\n", ("EA-TARGET",)),
    ("TD --target-dir admitted with --plan", "    if a.target_dir is not None and not (a.embed_missing or a.embed_card):\n", "    if False:\n", ("EA-TARGET",)),
    ("TD copy under the raw basename (card)", "    copy = os.path.join(os.path.abspath(target_dir), cache_file(arm))\n    source =",
     "    copy = os.path.join(os.path.abspath(target_dir), EG.cache_file_for(arm.model))\n    source =", ("EA-TARGET",)),
    ("TD reader ignores target_dir", "    if target_dir is not None:\n        return configure_arm_copy(FM, arm, data_root, target_dir)\n", "", ("EA-TREADER",)),
    ("TD reader configures the source", "    FM.configure_embedding(model=arm.model, cache_file=path)\n",
     "    FM.configure_embedding(model=arm.model, cache_file=os.path.join(data_root, cache_file(arm)))\n", ("EA-TREADER",)),
    ("TD reader path pin not installed", "    pin_copy_connect(path)\n    return path\n", "    return path\n", ("EA-TREADER",)),
    ("TD reader pin by basename only", "        if os.path.basename(p) == base and _norm(p) != want:\n", "        if False:\n", ("EA-TREADER",)),
    ("TD reader provenance sha unchecked", "    if sha != rec.get(\"sha256_after\"):\n", "    if False:\n", ("EA-TREADER",)),
    ("TD reader provenance path unchecked", " or _norm(rec.get(\"copy\") or \"\") != _norm(path):\n", ":\n", ("EA-TREADER",)),
    ("TD reader admits the source directory", "    if _norm(target_dir) == _norm(data_root):\n", "    if False:\n", ("EA-TREADER",)),
    # READY_emb_target 6202766 C-ET-1 / C-ET-3 / C-ET-4 (2026-09-29)
    ("ET1 raw copy not exclusive ('wb')", "    with open(source, \"rb\") as s, open(copy, \"xb\") as d:\n",
     "    with open(source, \"rb\") as s, open(copy, \"wb\") as d:\n", ("EA-TARGET",)),
    ("ET1 card file not created exclusively", "        open(path, \"xb\").close()                        # C-ET-1",
     "        open(path, \"ab\").close()                        # C-ET-1", ("EA-TARGET",)),
    ("ET3 flat_mix admission token not set", "    FM.ARM_COPY_ADMITTED = os.path.abspath(path)        # C-ET-3", "    pass        # C-ET-3", ("EA-TREADER",)),
    ("ET3 flat_mix admission token not cleared", "        FM.ARM_COPY_ADMITTED = None\n", "        pass\n", ("EA-TREADER",)),
    ("ET3 open_arm_reader reads without a DIR", "    if target_dir is None:\n        refuse(\"arm %s is read only",
     "    if False:\n        refuse(\"arm %s is read only", ("EA-TREADER",)),
    ("ET4 registrar pin not checked", "    registrar_pin(arm, sha)\n", "", ("EA-TREADER",)),
    ("ET4 pin file absence tolerated", "    if not os.path.isfile(pf):\n", "    if False:\n", ("EA-TREADER",)),
    ("ET4 schema unchecked", "pins.get(\"schema\") != ARM_PINS_SCHEMA or ", "", ("EA-TREADER",)),
    ("ET4 null pin admitted", "    if not want:\n", "    if False:\n", ("EA-TREADER", "EA-PINFILE")),
    ("ET4 pin mismatch admitted", "    if want != sha:\n", "    if False:\n", ("EA-TREADER",)),
    ("TD reader admits qwen3 via a copy", "    if arm.name == \"qwen3_raw\":\n        refuse(\"qwen3_raw is the DB of record", "    if False:\n        refuse(\"qwen3_raw is the DB of record", ("EA-TREADER",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut = src.index("\nMUTANTS = (")
    head, tail = src[:cut], src[cut:]
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "embedder_arms_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new) + tail, "<mutant>", "exec"), ns)
            ns["selftest"](only=set(tests), quiet=True)
            res = "SURVIVED"
        except BaseException as e:            # noqa: B902
            root = e                          # the first failing check, not a temp-dir cleanup error chained on top of it
            while not isinstance(root, (AssertionError, SystemExit)) and root.__context__ is not None:
                root = root.__context__
            res = "KILLED | %s" % str(root if isinstance(root, (AssertionError, SystemExit)) else e)[:100]
        killed += res.startswith("KILLED")
        print("  %-40s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


# ------------------------------------------------------------------------------------------------ inertness (absent flag)
BASE_BLOB = "4f56e79d32a97ad04d7e2b1582c3660d471e0c57"   # tools/analysis/embedder_arms.py at main 532dd1d (git blob, LF)
INERT_ARGV = (["--embed-missing", "gemma_raw", "--expect-missing", "2"], ["--embed-missing", "gemma_raw", "--expect-missing", "5"],
              ["--embed-missing", "gemma_raw", "--expect-missing", "2", "--go"], ["--embed-missing", "gemma_raw", "--expect-missing", "0"],
              ["--embed-missing", "nomic_raw", "--expect-missing", "22"], ["--embed-missing", "nomic_raw", "--expect-missing", "22", "--go"],
              ["--embed-card", "nomic_card"], ["--embed-card", "nomic_card", "--go"], ["--embed-card", "gemma_card", "--go"],
              ["--embed-card", "gemma_card", "--go"], ["--plan", "--go"], ["--plan"])


def _inert_leg(src, tag, log):
    """exec one rendering in a fresh namespace; run INERT_ARGV through its main() with NO --target-dir on a synthetic data root
    (stub Ollama via OLLAMA_HOST, stub pool guard, stub needed_texts); -> (records, file sha256s, posts, namespace)."""
    ns = {"__name__": "embedder_arms_leg_" + tag, "__file__": os.path.abspath(__file__)}
    exec(compile(src, "<leg %s>" % tag, "exec"), ns)
    base_t = ["s%02d" % i for i in range(25)]
    texts = base_t + ["new1", "new2"]
    saved = (pool_guard.DATA_ROOT, pool_guard.assert_pool_of_record)
    counts = {}
    for fn in ("resolve_target", "run_embed", "check_target_flag"):
        if fn in ns:
            def wrap(*a, _f=ns[fn], _n=fn, **k):
                counts.setdefault(_n, []).append(a[2] if _n == "resolve_target" else getattr(a[0], "target_dir", "?"))
                return _f(*a, **k)
            ns[fn] = wrap
    with tempfile.TemporaryDirectory() as td:
        root = os.path.join(td, "root")
        os.makedirs(root)
        norm = lambda s: (s or "").replace(td, "<TD>")
        try:
            pool_guard.DATA_ROOT = root
            pool_guard.assert_pool_of_record = lambda pid, *a, **k: print("[POOL] %s (stub: inertness, synthetic)" % pid)
            ns["needed_texts"] = lambda: list(texts)
            n0 = len(log)
            recs = [_capture(lambda: ns["write_vectors"](os.path.join(root, ns["cache_file"](ns["ARMS"]["gemma_raw"])),
                                                         ns["ARMS"]["gemma_raw"], base_t, ns["ollama_embed"])),
                    _capture(lambda: ns["write_vectors"](os.path.join(root, ns["cache_file"](ns["ARMS"]["nomic_raw"])),
                                                         ns["ARMS"]["nomic_raw"], base_t[:5], ns["ollama_embed"]))]
            recs += [_capture(lambda: ns["main"](list(argv))) for argv in INERT_ARGV]
            calls = []

            class FMStub(object):
                @staticmethod
                def configure_embedding(cache_file=None, model=None):
                    calls.append((norm(cache_file), model))
            recs += [_capture(lambda: ns["configure_arm"](FMStub, a, root)) for a in ns["ARMS"].values()]
            recs = [(norm(o), norm(e), norm(r) if isinstance(r, str) else r) for o, e, r in recs] + [("configure_embedding", repr(calls), None)]
            shas = sorted((os.path.relpath(os.path.join(dp, f), td), _sha(os.path.join(dp, f))) for dp, _d, fs in os.walk(td) for f in fs)
        finally:
            pool_guard.DATA_ROOT, pool_guard.assert_pool_of_record = saved
    return recs, shas, [(p, m, list(i)) for p, m, i in log[n0:]], counts


def inertness():
    """EMB-TARGET-DIR absent-flag proof: the base rendering (BASE_BLOB, main 532dd1d) and this file run the SAME pre-existing modes
    (INERT_ARGV through main(), write_vectors, configure_arm on every arm) with no --target-dir; stdout, refusals, return values,
    every file's sha256 and every stub-Ollama request must be identical. Discriminator: leg B EXECUTED the new code
    (resolve_target / run_embed / check_target_flag called, target_dir None each time); leg A has none of them."""
    import subprocess
    root = os.path.dirname(os.path.dirname(HERE))
    base = subprocess.run(["git", "cat-file", "blob", BASE_BLOB], cwd=root, capture_output=True, check=True).stdout
    got = hashlib.sha1(b"blob %d\x00" % len(base) + base).hexdigest()
    if got != BASE_BLOB:
        refuse("base blob mismatch: %s != %s" % (got, BASE_BLOB))
    mine = open(os.path.abspath(__file__), "rb").read().replace(b"\r\n", b"\n")
    saved_host = os.environ.get("OLLAMA_HOST")
    with stub_ollama() as (url, log, _state):
        os.environ["OLLAMA_HOST"] = url[:-len("/api/embed")]
        try:
            A = _inert_leg(base.decode("utf-8"), "A", log)
            B = _inert_leg(mine.decode("utf-8"), "B", log)
        finally:
            if saved_host is None:
                os.environ.pop("OLLAMA_HOST", None)
            else:
                os.environ["OLLAMA_HOST"] = saved_host
    same = [A[k] == B[k] for k in range(3)]
    print("[INERT] leg A blob:%s (main 532dd1d); leg B blob:%s (this file, LF)" % (BASE_BLOB[:8], _script_blob()[:8]))
    print("[INERT] %d records (stdout, refusal, return) identical: %s; %d files sha256 identical: %s; %d stub-Ollama requests identical: %s"
          % (len(B[0]), same[0], len(B[1]), same[1], len(B[2]), same[2]))
    refusals = sum(1 for r in B[0] if r[1])
    print("[INERT] of which refusals %d; files in the leg's tree %d; discriminator: leg A new-code calls %s; leg B %s"
          % (refusals, len(B[1]), {k: len(v) for k, v in A[3].items()},
             {k: "%d (target_dir %s)" % (len(v), sorted(set(map(repr, v)))) for k, v in B[3].items()}))
    for k in range(3):
        if not same[k]:
            for i, (x, y) in enumerate(zip(A[k], B[k])):
                if x != y:
                    print("[INERT] DIFF part %d item %d:\n  A %r\n  B %r" % (k, i, x, y))
                    break
    disc = (not A[3] and len(B[3].get("resolve_target", [])) > 0 and set(map(repr, B[3]["resolve_target"])) == {"None"}
            and len(B[3].get("run_embed", [])) > 0 and len(B[3].get("check_target_flag", [])) > 0)
    ok_all = all(same) and disc and len(B[2]) > 0 and refusals > 0
    print("[INERT] %s" % ("INERT: identical with the flag absent; leg B executed the new code" if ok_all else "NOT INERT"))
    return 0 if ok_all else 1


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--inertness", action="store_true")
    g.add_argument("--plan", action="store_true")
    g.add_argument("--embed-missing", choices=sorted(a for a in ARMS if not ARMS[a].role == "SECONDARY" and a != "qwen3_raw"))
    g.add_argument("--embed-card", choices=sorted(a for a in ARMS if ARMS[a].role == "SECONDARY"))
    ap.add_argument("--expect-missing", type=int, default=None)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--target-dir", default=None, help="EMB-TARGET-DIR: write only to a copy DIR/<the arm's cache file name> "
                    "(a raw arm: the source copied, sha256 recorded; a card arm: a NEW file); the source is never a target")
    a = ap.parse_args(argv)
    if a.selftest or a.mutants or a.inertness:
        print("pool %s (selftest: synthetic only; the pool is not read)" % POOL_ID)
    else:
        pool_guard.assert_pool_of_record(POOL_ID)
    print("[THREADS] " + " ".join("%s=%s" % (v, os.environ.get(v)) for v in THREAD_VARS))
    if a.go and not (a.embed_missing or a.embed_card):
        refuse("--go is admitted with --embed-missing / --embed-card only")
    check_target_flag(a)
    if a.selftest:
        print("SELFTEST PASSED: %d checks" % selftest())
        return 0
    if a.mutants:
        return run_mutants()
    if a.inertness:
        return inertness()
    if a.plan:
        return plan()
    return run_embed(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
