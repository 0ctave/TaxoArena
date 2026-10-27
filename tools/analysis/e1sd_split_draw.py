"""E1-SPLIT-DRAWS split-draw tool: three NEW CK-CLOSE-v1 content-closed MMLU-Pro splits (salts e1sd1, e1sd2, e1sd3; held-out
0.30), written as reservedPoolFile id files, and the six build TOMLs. ZERO judge / LLM / embedding calls; no JVM.

REGISTRATION OF RECORD: docs/judge_v2_program.md "## Registered 2026-10-03 (before any code or call) — E1-SPLIT-DRAWS: is E1's
nomic-vs-qwen3 anchor-free tree-filing loss consistently negative, and larger than the between-split spread, across K = 3 freshly
re-drawn CK-CLOSE content-closed MMLU-Pro splits ..." (L23831-L23859, written at a1c65848), HYGIENE line, verbatim in part:
"side = split_side.side_of_hash(side_hash(stem_key(text), salt)) with salts "e1sd1", "e1sd2", "e1sd3" (fixed now), held-out 0.30 /
TRAIN 0.70 (af_clean_s42's 70 / 30 structure; the engine's GATE drawn inside TRAIN as for af_clean_s42); exact norm-v1 duplicates
share a side (content-closed by construction); near-copies counted and disclosed. Each split is written as a reservedPoolFile
(experiment_configs/e1_split_draws/reserved_pool_e1sd<k>.json, sha256 printed); these pools are NEVER arena pools (no judge reads
them; never a pool of record) and are never compared with p2dca's 3,445."

BUILDER DECLARATIONS (none changes a registered word; for the registrar):
  S1 the salt is side_hash's second argument (the place NORMALISER_VERSION takes in tier b): h = uint64(sha256(salt U+001F
     stem_key(text))[:8]) mod 1000; held-out = split_side.side_of_hash(h) == EVAL (h < 300); TRAIN = GATE + TRAIN (h >= 300),
     0.70. The engine then draws its own GATE inside TRAIN with the UNSALTED hash (SplitSide.gateOf), as for af_clean_s42.
  S2 the corpus is EXACTLY the rows the engine loads for datasetType MMLU_PRO (MMLUDatasetFetcher.loadFromDb): mmlu_pro LEFT JOIN
     eval_question_link ON m.id = l.mmlu_pro_row_id ORDER BY m.id; engine id = the eval question_id when linked (> 0), else the
     sentinel -1,000,000 - mmlu_pro.id (UNLINKED_QUERY_ID_BASE); domain = formatData's title-casing. A row whose text is blank
     REFUSES (the engine drops it; a Python/Kotlin whitespace disagreement must not decide a side). The file lists EVERY held-out
     row's engine id (sentinels included: they are routing-only members on the test side, as in p2dca's file); the pool id is
     pool_guard.compute_pool_id over the judgeable ids (ReservedPool.computePoolId; sentinels excluded).
  S3 CLOSURE, printed per split (CK-CLOSE-v1 = stem_key closure, global, sentinels included, family closure, twins clustered):
     |stem keys(held-out) & stem keys(TRAIN)| = 0, |texts(held-out) & texts(TRAIN)| = 0 and the engine's finishSplit content-
     closure move count = 0 (re-computed here; the build log must then carry no [SPLIT-CLOSURE] line and closedByContent=0).
     Global: the side is a pure function of stem_key, so any copy of a held-out key in ANY corpus would take the same side under
     this salt. Family closure: MMLU-Pro carries no family id (n/a, printed). Twins inside held-out are clustered by the readout
     (stem_key groups; Kish m-bar printed), never dropped.
  S4 NEAR-COPIES (disclosed, never removed): held-out texts whose nearest TRAIN text has cosine >= 0.98 in qwen3 at 512 dims
     (the record's NEAR_COS / slice, intent_transfer_s0.near_copies), read from embeddings_cache.db through pool_guard.open_ro.
  S5 NEVER A POOL OF RECORD: the pool id must differ from p2dca21ab5f4ef3ae and from every registry pool (reserved_pools.json),
     the three ids must be distinct, and none is ever added to the registry. Pool state in the corpus DB: FRESH (no rows: before a
     split's first build), RECORDED (rows == the file's judgeable ids: after it), anything else REFUSES (CONFLICT).
  S6 the six TOMLs = a header, the line '# ---- BASE ----', then experiment_configs/anchorfree/redraw/af_clean_s42.toml line for
     line (LF) except EXACTLY THREE active key lines: outputDir = "experiment_results/e1_split_draws/<N|Q>_e1sd<k>",
     reservedPoolFile = "experiment_configs/e1_split_draws/reserved_pool_e1sd<k>.json", pool = "<that file's pool id>" (the
     engine's [POOL-PIN]: the JVM refuses unless its split hashes to it). N and Q TOMLs of a split differ ONLY in outputDir; the
     embedder is set by the launcher (tools/analysis/e1sd_launch.py), never by a key. One seed (42) per TOML; never `seeds = [...]`.

LAUNCH SEQUENCE (engine-coder, then the run-operator; zero calls):
  python tools/analysis/e1sd_split_draw.py --selftest      # fixture corpus; every check and refusal executed with VALUE asserts
  python tools/analysis/e1sd_split_draw.py --mutants       # every declared mutant must be KILLED by the selftest
  python tools/analysis/e1sd_split_draw.py --write         # ONCE (engine-coder): the three id files, mode x (refuses if any exists)
  python tools/analysis/e1sd_split_draw.py --write-configs # ONCE (engine-coder): the six TOMLs, mode x, from the files' pool ids
  python tools/analysis/e1sd_split_draw.py --check         # anyone: re-derive from the DB, byte-compare the committed files, sizes,
                                                           # closure, near-copies, pool state, the six TOMLs (rc 0 / 2)
  Set TAXOARENA_DATA_ROOT to the main checkout when running from a worktree. A pool reader (rule 7): never during a construction.
  --corpus-db <path> (any mode reading the DB) reads a checkpointed scratch copy instead (the launcher's use; never written here).

MUTANTS: see MUTANTS below (the table with results is in the commit message).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):     # BEFORE numpy: single-threaded CPU lane
    os.environ[_v] = "1"

import io
import re
import sys
import json
import struct
import sqlite3
import hashlib
import argparse
import tempfile
import contextlib
import subprocess
from collections import OrderedDict, Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard  # noqa: E402
import split_side as SS  # noqa: E402

TAG = "[E1SD-SPLIT]"
SALTS = ("e1sd1", "e1sd2", "e1sd3")
CFG_REL = "experiment_configs/e1_split_draws"
SPLIT_REL = CFG_REL + "/reserved_pool_e1sd%d.json"
TOML_REL = CFG_REL + "/%s_e1sd%d.toml"
OUT_REL = "experiment_results/e1_split_draws/%s_e1sd%d"
ARMS = ("N", "Q")
ARM_EMBEDDER = {"N": "nomic_raw (nomic-embed-text:latest, the pinned DIR arm file through e1_route_launch's working copy)",
                "Q": "qwen3 (qwen3-embedding:latest, embeddings_cache.db of record)"}
BASE_TOML = "experiment_configs/anchorfree/redraw/af_clean_s42.toml"
MARK = "# ---- BASE ----"
CHANGED_KEYS = ("outputDir", "reservedPoolFile", "pool")
CORPUS_DB = "mmlu_pro_dataset_cache_v2.db"
EMB_DB = "embeddings_cache.db"
P2DCA = "p2dca21ab5f4ef3ae"
UNLINKED_BASE = -1000000
HELD_OUT_SIDE = SS.EVAL
NEAR_COS = 0.98
NEAR_DIM = 512
ENGINE_SQL = ("SELECT m.id, m.question, m.category, l.question_id FROM mmlu_pro m LEFT JOIN eval_question_link l "
              "ON m.id = l.mmlu_pro_row_id ORDER BY m.id ASC")


class Refused(SystemExit):
    pass


def refuse(msg):
    print("%s REFUSED: %s" % (TAG, msg))
    raise Refused("%s REFUSED: %s" % (TAG, msg))


def blob_lf(path):
    with open(path, "rb") as f:
        d = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_lf(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def rel(p):
    return os.path.join(ROOT, *p.split("/"))


# ------------------------------------------------------------------------------------------------ the corpus (S2)
def engine_domain(cat):
    """MMLUDatasetFetcher.formatData: split on '_' and '-', first char title-cased, joined by one space."""
    c = cat if cat is not None else "Unknown"
    return " ".join((w[:1].upper() + w[1:]) if w[:1].islower() else w for w in re.split(r"[_-]", c))


def corpus_rows(con):
    """-> list of dict(row, id, text, category, domain) in the engine's load order (S2)."""
    out, blank = [], []
    for rid, q, cat, qid in con.execute(ENGINE_SQL):
        if q is None or q.strip() == "":
            blank.append(rid)
            continue
        eid = qid if (qid is not None and qid > 0) else UNLINKED_BASE - rid
        out.append(dict(row=rid, id=eid, text=q, category=(cat or "unknown").lower(), domain=engine_domain(cat)))
    if blank:
        refuse("%d mmlu_pro row(s) carry a blank question (first rows %s): the engine drops them; refusing rather than letting a "
               "whitespace rule decide a side" % (len(blank), blank[:5]))
    ids = Counter(r["id"] for r in out)
    dup = [i for i, n in ids.items() if n > 1]
    if dup:
        refuse("%d engine id(s) occur on several loaded rows (first %s)" % (len(dup), sorted(dup)[:5]))
    return out


def side(text, salt, memo=None):
    if memo is not None and text in memo:
        return memo[text]
    s = SS.side_of_hash(SS.side_hash(SS.stem_key(text), salt))
    if memo is not None:
        memo[text] = s
    return s


def draw(rows, salt):
    """One split: held-out rows (side EVAL under the salt) and TRAIN rows (GATE + TRAIN). The file lists every held-out row's
    engine id by domain, domains in first-appearance order, ids in row order."""
    memo = {}
    held, train = [], []
    for r in rows:
        (held if side(r["text"], salt, memo) == HELD_OUT_SIDE else train).append(r)
    ids = OrderedDict()
    for r in held:
        ids.setdefault(r["domain"], []).append(r["id"])
    return dict(salt=salt, held=held, train=train, ids=ids, pool=pool_guard.compute_pool_id(pool_guard.judgeable(ids)))


def file_bytes(ids):
    return (json.dumps(ids, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def distinct(rows):
    """-> [(text, category)] one entry per distinct text, its first row's category (anchor_free_readout.corpus's rule)."""
    seen = OrderedDict()
    for r in rows:
        seen.setdefault(r["text"], r["category"])
    return list(seen.items())


def multi_category_texts(rows):
    cats = {}
    for r in rows:
        cats.setdefault(r["text"], set()).add(r["category"])
    return sum(1 for v in cats.values() if len(v) > 1)


def closure(d):
    """S3 -> dict of the three closure counts (each must be 0) and the id overlap."""
    hk = set(SS.stem_key(r["text"]) for r in d["held"])
    tk = set(SS.stem_key(r["text"]) for r in d["train"])
    ht = set(r["text"] for r in d["held"])
    tt = set(r["text"] for r in d["train"])
    moves = sum(1 for r in d["train"] if SS.stem_key(r["text"]) in hk)
    ids = set(r["id"] for r in d["held"]) & set(r["id"] for r in d["train"])
    return dict(key_overlap=len(hk & tk), text_overlap=len(ht & tt), engine_moves=moves, id_overlap=len(ids))


def gate_prediction(d):
    """SplitSide.gateOf over the TRAIN id -> text map, UNSALTED (the engine's GATE inside TRAIN)."""
    return sum(1 for r in d["train"] if SS.GATE_LOWER <= SS.side_hash(SS.stem_key(r["text"])) < SS.GATE_UPPER)


def kish_mbar_texts(texts):
    c = Counter(SS.stem_key(t) for t in texts)
    v = np.array(list(c.values()), dtype=np.float64)
    return float((v ** 2).sum() / v.sum()), len(c)


def near_copies(held_texts, train_texts, vec):
    """S4: held-out texts whose nearest TRAIN text has cos >= NEAR_COS (unit vectors at NEAR_DIM). -> (count, n scored)."""
    h = [t for t in held_texts if t in vec]
    tr = [t for t in train_texts if t in vec]
    if not h or not tr:
        return 0, len(h)
    T = np.stack([vec[t] for t in tr])
    n = 0
    for s in range(0, len(h), 1000):
        H = np.stack([vec[t] for t in h[s:s + 1000]])
        n += int(((H @ T.T).max(1) >= NEAR_COS).sum())
    return n, len(h)


def qwen3_512(texts, emb_db):
    want, vec = set(texts), {}
    con = pool_guard.open_ro(emb_db)
    try:
        for t, b in con.execute("SELECT query, vector FROM embeddings"):
            if t in want and isinstance(b, bytes) and len(b) >= 4 * NEAR_DIM:
                v = np.array(struct.unpack(">%df" % NEAR_DIM, b[:4 * NEAR_DIM]), dtype=np.float64)
                nv = float(np.linalg.norm(v))
                if nv > 0:
                    vec[t] = v / nv
    finally:
        con.close()
    return vec


# ------------------------------------------------------------------------------------------------ pool state (S5)
def forbidden_pools():
    return {P2DCA} | set(pool_guard.load_registry())


def pool_state(con, pid, ids):
    """FRESH (no rows) / RECORDED (rows == the file's judgeable (domain, id) set); anything else REFUSES."""
    rows = pool_guard.pool_rows(con, pid)
    if not rows:
        return "FRESH"
    want = {(k, q) for k, v in pool_guard.judgeable(ids).items() for q in v}
    got = {(k, q) for k, v in rows.items() for q in v}
    if got != want:
        refuse("CONFLICT: pool %s has %d reserved_pool rows that differ from its file's %d judgeable ids by %d entries"
               % (pid, len(got), len(want), len(got ^ want)))
    return "RECORDED"


def check_pool_ids(draws, forbidden):
    pids = [d["pool"] for d in draws]
    for d in draws:
        if d["pool"] in forbidden:
            refuse("split %s hashes to %s, a pool of record / registry pool: these splits are NEVER pools of record"
                   % (d["salt"], d["pool"]))
    if len(set(pids)) != len(pids):
        refuse("the split pool ids are not distinct: %s" % pids)
    return pids


# ------------------------------------------------------------------------------------------------ the report
def report(draws, out, vec=None, con=None, forbidden=None, p2dca_texts=None):
    """Prints sizes, closure, near-copies, pool state; REFUSES on any closure breach. -> list of per-split summaries."""
    forbidden = forbidden_pools() if forbidden is None else forbidden
    check_pool_ids(draws, forbidden)
    summ = []
    for k, d in enumerate(draws, 1):
        nh, nt = len(d["held"]), len(d["train"])
        hd, td = distinct(d["held"]), distinct(d["train"])
        judge = sum(1 for r in d["held"] if r["id"] > 0)
        sent = nh - judge
        cl = closure(d)
        mbar, groups = kish_mbar_texts([t for t, _ in hd])
        gate = gate_prediction(d)
        fb = file_bytes(d["ids"])
        out("%s split %d salt %s -> pool %s (file sha256-lf %s, %d bytes; NEVER a pool of record: != %s, not in the registry)"
            % (TAG, k, d["salt"], d["pool"], sha256_lf(fb), len(fb), P2DCA))
        out("%s   SIZES rows: held-out %d / TRAIN %d of %d (held-out fraction %.4f; registered 0.30); judgeable held-out ids %d, "
            "sentinels %d; DISTINCT TEXTS (the readout's denominators): held-out %d / TRAIN %d; held-out stem_key groups %d, "
            "Kish m-bar %.4f; engine GATE inside TRAIN (unsalted gateOf) %d rows -> manifest train_size %d, test_size %d, gate_size %d"
            % (TAG, nh, nt, nh + nt, nh / float(nh + nt), judge, sent, len(hd), len(td), groups, mbar, gate, nt, nh, gate))
        fr = sorted((len([r for r in d["held"] if r["domain"] == dom]) / float(len([r for r in d["held"] + d["train"] if r["domain"] == dom])), dom)
                    for dom in sorted(set(r["domain"] for r in d["held"] + d["train"])))
        out("%s   per-domain held-out fraction: min %.3f (%s), max %.3f (%s) over %d domains"
            % (TAG, fr[0][0], fr[0][1], fr[-1][0], fr[-1][1], len(fr)))
        out("%s   CLOSURE (CK-CLOSE-v1): stem_key overlap held-out/TRAIN %d; exact-text overlap %d; engine finishSplit closure moves "
            "%d (=> closedByContent=0, no [SPLIT-CLOSURE] line); id overlap %d; family closure n/a (MMLU-Pro has no family id); "
            "global by construction (side = f(stem_key, salt))" % (TAG, cl["key_overlap"], cl["text_overlap"], cl["engine_moves"],
                                                                     cl["id_overlap"]))
        if cl["key_overlap"] or cl["text_overlap"] or cl["engine_moves"] or cl["id_overlap"]:
            refuse("split %s is NOT content-closed: %s" % (d["salt"], cl))
        nc = None
        if vec is not None:
            nc, nsc = near_copies([t for t, _ in hd], [t for t, _ in td], vec)
            out("%s   NEAR-COPIES: %d of %d held-out texts (scored %d) have a TRAIN neighbour at cos >= %.2f (qwen3 %d); disclosed, "
                "not removed" % (TAG, nc, len(hd), nsc, NEAR_COS, NEAR_DIM))
        st = None
        if con is not None:
            st = pool_state(con, d["pool"], d["ids"])
            out("%s   POOL STATE in the corpus DB: %s" % (TAG, st))
        if p2dca_texts is not None:
            ov = len(set(t for t, _ in hd) & p2dca_texts)
            out("%s   descriptive only: %d of its held-out texts are among p2dca's held-out texts (never compared with p2dca's 3,445)"
                % (TAG, ov))
        summ.append(dict(k=k, salt=d["salt"], pool=d["pool"], held_rows=nh, train_rows=nt, held_texts=len(hd), train_texts=len(td),
                         judgeable=judge, sentinels=sent, gate=gate, closure=cl, near=nc, state=st, mbar=mbar, groups=groups,
                         sha=sha256_lf(fb)))
    for a in range(len(draws)):
        for b in range(a + 1, len(draws)):
            ha = set(r["text"] for r in draws[a]["held"])
            hb = set(r["text"] for r in draws[b]["held"])
            out("%s pairwise: held-out texts shared by splits %d and %d: %d (independent salts: about 0.30 x %d expected)"
                % (TAG, a + 1, b + 1, len(ha & hb), len(ha)))
    return summ


# ------------------------------------------------------------------------------------------------ TOMLs (S6)
def toml_text(arm, k, pid, base_text):
    od = OUT_REL % (arm, k)
    lines = base_text.replace("\r\n", "\n").split("\n")
    repl = {"outputDir": 'outputDir     = "%s"' % od,
            "reservedPoolFile": 'reservedPoolFile = "%s"' % (SPLIT_REL % k),
            "pool": 'pool             = "%s"   # [POOL-PIN] guard: the JVM refuses unless its split hashes to this split\'s pool' % pid}
    done = set()
    out = []
    for ln in lines:
        key = ln.split("=", 1)[0].strip() if ("=" in ln and not ln.lstrip().startswith("#")) else None
        if key in repl:
            out.append(repl[key])
            done.add(key)
        else:
            out.append(ln)
    if done != set(CHANGED_KEYS):
        refuse("the base TOML lacks key line(s) %s" % sorted(set(CHANGED_KEYS) - done))
    head = [
        "# E1-SPLIT-DRAWS build %s_e1sd%d: embedder %s; split e1sd%d (salt \"%s\", pool %s; never a pool of record)."
        % (arm, k, "nomic_raw" if arm == "N" else "qwen3", k, SALTS[k - 1], pid),
        "# Registration: docs/judge_v2_program.md \"## Registered 2026-10-03 (before any code or call) — E1-SPLIT-DRAWS: ...\"",
        "# (L23831-L23859, a1c65848): builds N_k (nomic_raw) and Q_k (qwen3), af_clean_s42's recipe, construction seed 42, one TOML",
        "# per build. = experiment_configs/anchorfree/redraw/af_clean_s42.toml byte for byte below the '# ---- BASE ----' line (LF),",
        "# except EXACTLY three active key lines: outputDir, reservedPoolFile (this split's id file) and pool (its id; the engine's",
        "# [POOL-PIN]). The BASE comments below are af_clean_s42's own and describe ITS split (p2dca), not this build's.",
        "# The embedder is NOT a key: tools/analysis/e1sd_launch.py sets it (N through e1_route_launch's working copy of the pinned",
        "# nomic_raw DIR file; Q reads embeddings_cache.db). Launch ONLY through that launcher, from the main checkout, one build per",
        "# rule-7 window, backup first, 12 threads; never `seeds = [...]`. Checked by tools/analysis/e1sd_split_draw.py --check.",
        "# Outputs are never committed (pinned by sha256, backed up to E: with SHA256SUMS.txt).",
        MARK,
    ]
    return "\n".join(head + out)


def check_toml(arm, k, pid, text, base_text):
    """S6: text and parsed-key diff against the base; refuses on any deviation. -> the parsed config."""
    import tomllib
    t = text.replace("\r\n", "\n")
    if MARK not in t.split("\n"):
        refuse("%s_e1sd%d: no BASE marker line" % (arm, k))
    body = t.split("\n")[t.split("\n").index(MARK) + 1:]
    base = base_text.replace("\r\n", "\n").split("\n")
    if len(body) != len(base):
        refuse("%s_e1sd%d: %d body lines, the base has %d" % (arm, k, len(body), len(base)))
    diff = [i for i, (a, b) in enumerate(zip(body, base)) if a != b]
    keys = sorted(base[i].split("=", 1)[0].strip() for i in diff)
    if keys != sorted(CHANGED_KEYS):
        refuse("%s_e1sd%d: the differing body lines are the base's %s, not exactly %s" % (arm, k, keys, sorted(CHANGED_KEYS)))
    cfg = tomllib.loads(t)
    bcfg = tomllib.loads("\n".join(base))
    kd = sorted(x for x in set(cfg) | set(bcfg) if cfg.get(x) != bcfg.get(x))
    if kd != sorted(CHANGED_KEYS):
        refuse("%s_e1sd%d: parsed key diff %s != %s" % (arm, k, kd, sorted(CHANGED_KEYS)))
    want = {"outputDir": OUT_REL % (arm, k), "reservedPoolFile": SPLIT_REL % k, "pool": pid}
    for key, v in want.items():
        if cfg.get(key) != v:
            refuse("%s_e1sd%d: %s = %r, expected %r" % (arm, k, key, cfg.get(key), v))
    if "seeds" in cfg or cfg.get("seed") != 42 or cfg.get("anchorFree") is not True:
        refuse("%s_e1sd%d: seed / seeds / anchorFree differ from the recipe" % (arm, k))
    return cfg


# ------------------------------------------------------------------------------------------------ a finished build (shared)
EXPECT_MODEL = {"N": "nomic-embed-text:latest", "Q": "qwen3-embedding:latest"}
SNAP_RE = re.compile(r"Snapshot ID: (\S+)")
POOL_LINE_RE = re.compile(r"\[POOL\] recorded (p[0-9a-f]{16}) \(seed=\S+, gate=(\d+), closedByContent=(\d+)\)")


def run_dir_of(arm, k, droot):
    return os.path.join(droot, *(OUT_REL % (arm, k)).split("/"), "seed_42")


def check_run_dir(rd, arm, k, d, config_blob, nomic_pin=None):
    """A finished build's run dir against its split d (draw()) and its declared config: manifest (pool, embedder, anchor-free,
    seed, no shuffle, completed, train / test / gate sizes == the split's), diagnostics/config.toml blob == declared, the log's
    [POOL] line (closedByContent=0, the gate), no [SPLIT-CLOSURE] line, the [TRAIN-ONLY] after-construction line, ONE snapshot id.
    -> dict(snapshot, manifest, log_pool_line); REFUSES on any finding (all findings printed in the message)."""
    mp = os.path.join(rd, "diagnostics", "run_manifest.json")
    lp = os.path.join(rd, "headless_run.log")
    if not (os.path.isfile(mp) and os.path.isfile(lp) and os.path.isfile(os.path.join(rd, "dag_snapshots.jsonl"))):
        refuse("%s_e1sd%d: run dir %s lacks manifest / log / dag_snapshots.jsonl" % (arm, k, rd))
    with open(mp, encoding="utf-8") as f:
        man = json.load(f)
    with open(lp, "rb") as f:
        log = f.read().decode("utf-8", "replace")
    gate = gate_prediction(d)
    want = dict(reserved_pool_id=d["pool"], embedding_model=EXPECT_MODEL[arm], anchor_free=True, seed=42,
                construction_order_shuffle_seed=None, exit_reason="completed", train_size=len(d["train"]),
                test_size=len(d["held"]), gate_size=gate, corpus_size=len(d["train"]) + len(d["held"]))
    bad = ["%s %r != %r" % (key, man.get(key), v) for key, v in want.items() if man.get(key) != v]
    if arm == "N":
        if man.get("embedding_cache_source_sha256") != nomic_pin:
            bad.append("embedding_cache_source_sha256 %r != the nomic_raw pin %s" % (man.get("embedding_cache_source_sha256"), nomic_pin))
    elif man.get("embedding_cache_file") is not None or man.get("embedding_cache_source_sha256") is not None:
        bad.append("a qwen3 build names an explicit embedding cache file (%r)" % man.get("embedding_cache_file"))
    cb = blob_lf(os.path.join(rd, "diagnostics", "config.toml")) if os.path.isfile(os.path.join(rd, "diagnostics", "config.toml")) else None
    if cb != config_blob:
        bad.append("diagnostics/config.toml blob %s != declared %s" % (cb, config_blob))
    pl = POOL_LINE_RE.findall(log)
    if len(pl) != 1 or pl[0] != (d["pool"], str(gate), "0"):
        bad.append("[POOL] line(s) %s != (%s, gate %d, closedByContent 0)" % (pl, d["pool"], gate))
    if "[SPLIT-CLOSURE]" in log:
        bad.append("the log carries a [SPLIT-CLOSURE] line (the engine moved TRAIN rows: the split is not this file's closed split)")
    if "[TRAIN-ONLY] after construction: 0 EVAL texts" not in log:
        bad.append("no '[TRAIN-ONLY] after construction: 0 EVAL texts' line")
    snaps = SNAP_RE.findall(log)
    if len(snaps) != 1:
        bad.append("%d 'Snapshot ID:' lines (exactly 1 required)" % len(snaps))
    if bad:
        refuse("%s_e1sd%d run dir %s: %s" % (arm, k, rd, "; ".join(bad)))
    return dict(snapshot=snaps[0], manifest=man, pool_line=pl[0])


def fake_run_dir(rd, arm, k, d, config_text, nomic_pin="PIN", snapshot="SNAP_%s%d", nodes=None, man_over=None, log_extra="",
                 closed=0, train_only=True):
    """Selftest helper (also used by e1_split_draws.py): a run dir as the engine writes it, for split d."""
    os.makedirs(os.path.join(rd, "diagnostics"), exist_ok=True)
    man = dict(reserved_pool_id=d["pool"], embedding_model=EXPECT_MODEL[arm], anchor_free=True, seed=42,
               construction_order_shuffle_seed=None, exit_reason="completed", train_size=len(d["train"]), test_size=len(d["held"]),
               gate_size=gate_prediction(d), corpus_size=len(d["train"]) + len(d["held"]))
    if arm == "N":
        man.update(embedding_cache_file="work/x.db", embedding_cache_source_sha256=nomic_pin)
    man.update(man_over or {})
    with open(os.path.join(rd, "diagnostics", "run_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f)
    with open(os.path.join(rd, "diagnostics", "config.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(config_text)
    sid = snapshot % (arm, k) if "%" in snapshot else snapshot
    with open(os.path.join(rd, "headless_run.log"), "w", encoding="utf-8") as f:
        f.write("x [INFO ] HeadlessRunner - [POOL] recorded %s (seed=42, gate=%d, closedByContent=%d); nothing activated\n"
                % (d["pool"], gate_prediction(d), closed))
        if train_only:
            f.write("x [INFO ] HeadlessRunner - [TRAIN-ONLY] after construction: 0 EVAL texts among the tree's members (9 keys checked)\n")
        f.write(log_extra)
        f.write("x [INFO ] HeadlessRunner - Successfully generated and saved snapshot. Snapshot ID: %s\n" % sid)
    with open(os.path.join(rd, "dag_snapshots.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"iteration": 1, "nodes": nodes or []}) + "\n")
    return sid


# ------------------------------------------------------------------------------------------------ modes
def data_path(name, override=None):
    return override if override else os.path.join(pool_guard.DATA_ROOT, name)


def load_draws(corpus_db, out=print):
    con = pool_guard.open_ro(corpus_db)
    try:
        rows = corpus_rows(con)
    finally:
        con.close()
    mc = multi_category_texts(rows)
    out("%s corpus %s: %d rows loaded in the engine's order (%d linked, %d sentinel), %d distinct texts, %d texts carry several "
        "categories (first row's category kept); salts %s" % (TAG, corpus_db, len(rows), sum(1 for r in rows if r["id"] > 0),
                                                            sum(1 for r in rows if r["id"] <= 0), len(set(r["text"] for r in rows)),
                                                            mc, list(SALTS)))
    return rows, [draw(rows, s) for s in SALTS]


def write_splits(draws, root=ROOT, out=print):
    paths = [os.path.join(root, *(SPLIT_REL % k).split("/")) for k in range(1, len(draws) + 1)]
    for p in paths:
        if os.path.exists(p):
            refuse("%s exists: the split files are write-once (mode x)" % p)
    os.makedirs(os.path.dirname(paths[0]), exist_ok=True)
    for p, d in zip(paths, draws):
        with open(p, "xb") as f:
            f.write(file_bytes(d["ids"]))
        out("%s wrote %s (pool %s, sha256-lf %s)" % (TAG, p, d["pool"], sha256_lf(file_bytes(d["ids"]))))
    return paths


def compare_files(draws, root=ROOT, out=print):
    for k, d in enumerate(draws, 1):
        p = os.path.join(root, *(SPLIT_REL % k).split("/"))
        if not os.path.isfile(p):
            refuse("%s is ABSENT" % p)
        with open(p, "rb") as f:
            got = f.read().replace(b"\r\n", b"\n")
        if got != file_bytes(d["ids"]):
            refuse("%s differs from the re-derived split %s (sha256-lf %s vs %s)" % (p, d["salt"], sha256_lf(got),
                                                                                 sha256_lf(file_bytes(d["ids"]))))
        ids = json.loads(got.decode("utf-8"))
        if pool_guard.compute_pool_id(pool_guard.judgeable(ids)) != d["pool"]:
            refuse("%s does not hash to %s" % (p, d["pool"]))
        out("%s %s == the re-derived split %s (byte-equal, LF); blob:%s; pool %s" % (TAG, SPLIT_REL % k, d["salt"], blob_lf(p)[:8],
                                                                                     d["pool"]))


def write_configs(pids, root=ROOT, out=print):
    with open(os.path.join(root, *BASE_TOML.split("/")), encoding="utf-8") as f:
        base = f.read()
    paths = []
    for k, pid in enumerate(pids, 1):
        for arm in ARMS:
            p = os.path.join(root, *(TOML_REL % (arm, k)).split("/"))
            if os.path.exists(p):
                refuse("%s exists: the TOMLs are write-once (mode x)" % p)
            paths.append((p, toml_text(arm, k, pid, base)))
    for p, t in paths:
        with open(p, "x", encoding="utf-8", newline="\n") as f:
            f.write(t)
        out("%s wrote %s blob:%s" % (TAG, p, blob_lf(p)))
    return [p for p, _ in paths]


def check_configs(pids, root=ROOT, out=print):
    with open(os.path.join(root, *BASE_TOML.split("/")), encoding="utf-8") as f:
        base = f.read()
    blobs = {}
    for k, pid in enumerate(pids, 1):
        for arm in ARMS:
            p = os.path.join(root, *(TOML_REL % (arm, k)).split("/"))
            if not os.path.isfile(p):
                refuse("%s is ABSENT" % p)
            with open(p, encoding="utf-8") as f:
                check_toml(arm, k, pid, f.read(), base)
            blobs["%s_e1sd%d" % (arm, k)] = blob_lf(p)
            out("%s TOML %s OK: af_clean_s42 body with exactly %s changed (pool %s); blob:%s" % (TAG, TOML_REL % (arm, k),
                                                                                              list(CHANGED_KEYS), pid, blobs["%s_e1sd%d" % (arm, k)][:8]))
    return blobs


def p2dca_heldout_texts(corpus_db):
    con = pool_guard.open_ro(corpus_db)
    try:
        ids = pool_guard.eval_ids(P2DCA)
        return set(t for q, t in con.execute("SELECT question_id, question_text FROM eval_question_link") if q in ids)
    finally:
        con.close()


def main_check(corpus_db=None, write=False, out=print):
    cdb = data_path(CORPUS_DB, corpus_db)
    out("%s [SCRIPT] tools/analysis/e1sd_split_draw.py blob:%s" % (TAG, blob_lf(os.path.abspath(__file__))))
    pid0 = pool_guard.assert_pool_of_record(P2DCA)
    out("%s pool %s (pool_guard.assert_pool_of_record; read ONLY to show these splits are not it)" % (TAG, pid0))
    rows, draws = load_draws(cdb, out)
    if write:
        write_splits(draws, out=out)
    compare_files(draws, out=out)
    vec = qwen3_512(set(r["text"] for r in rows), data_path(EMB_DB))
    out("%s qwen3 vectors (512-d) for near-copies: %d of %d distinct texts" % (TAG, len(vec), len(set(r["text"] for r in rows))))
    con = pool_guard.open_ro(cdb)
    try:
        summ = report(draws, out, vec=vec, con=con, p2dca_texts=p2dca_heldout_texts(cdb))
    finally:
        con.close()
    return rows, draws, summ


# ------------------------------------------------------------------------------------------------ selftest
def _fixture_db(path, extra_rows=()):
    """A corpus DB with the engine's two tables: 400 rows over 3 categories, exact and norm-v1 twins, unlinked rows."""
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE mmlu_pro (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, category TEXT, cot_content TEXT, "
                "options TEXT, answer TEXT)")
    con.execute("CREATE TABLE eval_question_link (question_id INTEGER PRIMARY KEY, mmlu_pro_row_id INTEGER, question_text TEXT "
                "NOT NULL, has_embedding INTEGER NOT NULL DEFAULT 0)")
    con.execute("CREATE TABLE reserved_pool (pool_id TEXT NOT NULL, question_id INTEGER NOT NULL, domain TEXT NOT NULL, "
                "PRIMARY KEY (pool_id, question_id)) WITHOUT ROWID")
    cats = ["math", "computer science", "health"]
    rows = []
    for i in range(400):
        rows.append(("Question number %d about topic %d?" % (i, i % 7), cats[i % 3]))
    rows.append(("Question number 5 about topic 5?", "math"))          # exact twin of row 6 (category differs: first kept)
    rows.append(("  QUESTION number 7   about topic 0?", "computer science"))   # norm-v1 twin of row 8
    rows += list(extra_rows)
    for q, c in rows:
        con.execute("INSERT INTO mmlu_pro (question, category, cot_content, options, answer) VALUES (?, ?, '', '[]', 'A')", (q, c))
    for rid in range(1, len(rows) + 1):
        if rid % 10 != 3:                                               # every 10th row (3, 13, ...) unlinked -> sentinel
            con.execute("INSERT INTO eval_question_link VALUES (?, ?, ?, 0)", (5000 + rid, rid, "t"))
    con.commit()
    return con


def selftest(quiet=False):
    """Every check and refusal executed on a fixture DB, with VALUE assertions (never 'a line exists'):
    T1 engine ids: linked rows carry the eval id, unlinked rows -1,000,000 - row (row 3 -> -1000003); domains title-cased
       ('computer science' -> 'Computer science'); a blank row REFUSES; ENGINE_SQL is exactly loadFromDb's join and order.
    T2 the side: equals an INDEPENDENT recomputation (hashlib: sha256(salt U+001F stem_key)[:8] big-endian mod 1000 < 300) for every
       row; differs from the unsalted side on some rows; salts give different splits; boundary h = 299 held-out, 300 TRAIN.
    T3 closure: exact twins and norm-v1 twins land on one side (counts 0 asserted); a TAMPERED draw (one held-out row's twin moved
       to TRAIN) REFUSES with the counts printed; the engine-move count equals the number of tampered rows.
    T4 file bytes and pool id: deterministic; pool id == pool_guard.compute_pool_id over judgeable ids only (a sentinel added to the
       file leaves it unchanged); write is mode x (a second write REFUSES); compare_files REFUSES a tampered file.
    T5 pool ids: a draw hashing to p2dca / a registry pool REFUSES; two equal pool ids REFUSE; pool_state FRESH / RECORDED /
       CONFLICT (refuses) on reserved_pool rows; a RECORDED state needs ALL judgeable rows (one missing row -> CONFLICT).
    T6 near-copies: designed unit vectors, 2 of 4 held-out texts above 0.98 -> 2 (min-vs-max mutant: max(1) -> min(1) gives 0);
       a threshold change to > NEAR_COS on an exact 0.98 pair changes the count (inclusive >= asserted).
    T7 the report: sizes printed with the VALUES of the fixture (held-out rows, judgeable, sentinels, distinct texts, gate);
       the held-out fraction on 400 rows lies in [0.22, 0.38].
    T8 TOMLs: toml_text on the real af_clean_s42.toml passes check_toml with the three keys asserted by value; a 4th changed line,
       a changed seed, a missing key line, a wrong pool and a `seeds = [...]` each REFUSE."""
    n = [0]

    def ok(cond, what):
        n[0] += 1
        if not bool(cond):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)

    def refused(fn, needle):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                fn()
        except Refused as e:
            return needle in str(e)
        return False

    td = tempfile.mkdtemp(prefix="e1sd_split_")
    try:
        con = _fixture_db(os.path.join(td, "c.db"))
        rows = corpus_rows(con)
        # T1
        r3 = [r for r in rows if r["row"] == 3][0]
        r4 = [r for r in rows if r["row"] == 5][0]
        ok(r3["id"] == -1000003 and r4["id"] == 5005, "T1 engine ids: row 3 unlinked -> -1000003, row 5 linked -> 5005")
        ok(r4["category"] == "computer science" and r4["domain"] == "Computer science", "T1 domain 'Computer science'")
        ok(engine_domain("computer_science-x") == "Computer Science X", "T1 formatData title-casing on '_' and '-'")
        ok(ENGINE_SQL.endswith("LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id ORDER BY m.id ASC"), "T1 loadFromDb's join")
        ok(len(rows) == 402 and [r["row"] for r in rows] == list(range(1, 403)), "T1 402 rows in mmlu_pro.id order")
        con2 = _fixture_db(os.path.join(td, "b.db"), extra_rows=[("   ", "math")])
        ok(refused(lambda: corpus_rows(con2), "blank question"), "T1 a blank row REFUSES")
        con2.close()
        # T2
        def indep(text, salt):
            d = hashlib.sha256((salt + "\u001f" + SS.stem_key(text)).encode("utf-8")).digest()
            return (int.from_bytes(d[:8], "big") % 1000) < 300
        d1 = draw(rows, SALTS[0])
        held_set = set(r["row"] for r in d1["held"])
        ok(all((r["row"] in held_set) == indep(r["text"], SALTS[0]) for r in rows), "T2 side == independent salted recomputation (402 rows)")
        uns = set(r["row"] for r in rows if SS.side_of_hash(SS.side_hash(SS.stem_key(r["text"]))) == SS.EVAL)
        ok(uns != held_set, "T2 the salted split differs from the unsalted side")
        d2 = draw(rows, SALTS[1])
        ok(set(r["row"] for r in d2["held"]) != held_set and d1["pool"] != d2["pool"], "T2 salts e1sd1 / e1sd2 give different splits")
        ok(SS.side_of_hash(299) == HELD_OUT_SIDE and SS.side_of_hash(300) != HELD_OUT_SIDE, "T2 boundary 299 held-out, 300 TRAIN")
        # T3
        tw = [r for r in rows if r["text"] == "Question number 5 about topic 5?"]
        tw2 = [r for r in rows if SS.stem_key(r["text"]) == SS.stem_key("Question number 7 about topic 0?")]
        ok(len(tw) == 2 and len(tw2) == 2, "T3 fixture carries an exact twin and a norm-v1 twin")
        for salt in SALTS:
            dd = draw(rows, salt)
            hs = set(r["row"] for r in dd["held"])
            ok(len(set(r["row"] in hs for r in tw)) == 1 and len(set(r["row"] in hs for r in tw2)) == 1,
               "T3 %s: both twin pairs on one side" % salt)
            cl = closure(dd)
            ok(cl == dict(key_overlap=0, text_overlap=0, engine_moves=0, id_overlap=0), "T3 %s closure counts all 0" % salt)
        bad = draw(rows, SALTS[0])
        src_side, dst_side = ("held", "train") if any(r["row"] in held_set for r in tw) else ("train", "held")
        mover = [r for r in bad[src_side] if r["text"] == tw[0]["text"]][0]      # ONE of the two exact twins changes side
        bad[src_side].remove(mover)
        bad[dst_side].append(mover)
        clb = closure(bad)
        ok(clb["key_overlap"] == 1 and clb["engine_moves"] == 1, "T3 tampered draw: key overlap 1, engine moves 1")
        out = []
        ok(refused(lambda: report([bad, draw(rows, SALTS[1]), draw(rows, SALTS[2])], out.append, forbidden=set()),
                   "NOT content-closed"), "T3 report REFUSES the tampered draw")
        bad2 = draw(rows, SALTS[0])                                             # a NORM-V1 twin moved: no exact-text overlap
        src_side, dst_side = ("held", "train") if any(r["row"] in held_set for r in tw2) else ("train", "held")
        mover = [r for r in bad2[src_side] if r["row"] == tw2[0]["row"]][0]
        bad2[src_side].remove(mover)
        bad2[dst_side].append(mover)
        clb2 = closure(bad2)
        ok(clb2["text_overlap"] == 0 and clb2["key_overlap"] == 1 and clb2["engine_moves"] == 1,
           "T3 norm-v1 tamper: text overlap 0, key overlap 1, engine moves 1")
        ok(refused(lambda: report([bad2, draw(rows, SALTS[1]), draw(rows, SALTS[2])], out.append, forbidden=set()),
                   "NOT content-closed"), "T3 report REFUSES the norm-v1 tamper (an exact-text-only check would admit it)")
        # T4
        fb = file_bytes(d1["ids"])
        ok(fb == file_bytes(draw(rows, SALTS[0])["ids"]), "T4 file bytes deterministic")
        ids_s = json.loads(fb.decode("utf-8"))
        first = list(ids_s)[0]
        ids_s[first] = ids_s[first] + [-1999999]
        ok(pool_guard.compute_pool_id(pool_guard.judgeable(ids_s)) == d1["pool"], "T4 a sentinel added leaves the pool id unchanged")
        ids_j = json.loads(fb.decode("utf-8"))
        ids_j[first] = ids_j[first][1:] if ids_j[first][0] > 0 else ids_j[first][2:]
        ok(pool_guard.compute_pool_id(pool_guard.judgeable(ids_j)) != d1["pool"], "T4 a judgeable id removed changes the pool id")
        root = os.path.join(td, "root")
        os.makedirs(root)
        draws = [draw(rows, s) for s in SALTS]
        write_splits(draws, root=root, out=lambda s: None)
        ok(refused(lambda: write_splits(draws, root=root, out=lambda s: None), "write-once"), "T4 a second write REFUSES (mode x)")
        compare_files(draws, root=root, out=lambda s: None)
        p2 = os.path.join(root, *(SPLIT_REL % 2).split("/"))
        with open(p2, "rb") as f:
            orig = f.read()
        with open(p2, "wb") as f:
            f.write(orig.replace(b"\n ", b"\n  ", 1))
        ok(refused(lambda: compare_files(draws, root=root, out=lambda s: None), "differs from the re-derived"), "T4 tampered file REFUSES")
        # T5
        ok(refused(lambda: check_pool_ids(draws, {draws[1]["pool"]}), "NEVER pools of record"), "T5 a forbidden pool id REFUSES")
        ok(refused(lambda: check_pool_ids([draws[0], draws[0], draws[2]], set()), "not distinct"), "T5 equal pool ids REFUSE")
        ok(P2DCA in forbidden_pools() and "paeec37aa28063c75" in forbidden_pools(), "T5 forbidden = p2dca + registry")
        ok(pool_state(con, d1["pool"], d1["ids"]) == "FRESH", "T5 FRESH before rows exist")
        j = pool_guard.judgeable(d1["ids"])
        for dom, qs in j.items():
            for q in qs:
                con.execute("INSERT INTO reserved_pool VALUES (?, ?, ?)", (d1["pool"], q, dom))
        ok(pool_state(con, d1["pool"], d1["ids"]) == "RECORDED", "T5 RECORDED when rows == file")
        dom0 = list(j)[0]
        con.execute("DELETE FROM reserved_pool WHERE pool_id = ? AND question_id = ?", (d1["pool"], j[dom0][0]))
        ok(refused(lambda: pool_state(con, d1["pool"], d1["ids"]), "CONFLICT"), "T5 one missing row -> CONFLICT refuses")
        # T6
        e = np.eye(4)
        vec = {"h1": e[0], "h2": e[1], "h3": e[2], "h4": e[3],
               "t1": e[0], "t2": (0.98 * e[1] + np.sqrt(1 - 0.98 ** 2) * e[2]), "t3": (0.5 * e[0] + 0.5 * e[3]) / np.sqrt(0.5)}
        vec["t2"] = vec["t2"] / np.linalg.norm(vec["t2"])
        nc, ns = near_copies(["h1", "h2", "h3", "h4"], ["t1", "t2", "t3"], vec)
        ok(nc == 2 and ns == 4, "T6 near-copies 2 of 4 (h1 exact, h2 at cos 0.98 inclusive); got %d" % nc)
        # T7
        out = []
        summ = report(draws, out.append, forbidden=set())
        s1 = summ[0]
        ok(s1["held_rows"] == len(d1["held"]) and s1["judgeable"] == sum(1 for r in d1["held"] if r["id"] > 0)
           and s1["sentinels"] == sum(1 for r in d1["held"] if r["id"] <= 0), "T7 report sizes = the draw's values")
        ok(s1["held_texts"] == len(set(r["text"] for r in d1["held"])) and s1["gate"] == gate_prediction(d1), "T7 distinct texts, gate")
        line = [l for l in out if "SIZES rows: held-out %d / TRAIN %d of 402" % (s1["held_rows"], s1["train_rows"]) in l]
        ok(len(line) == 1, "T7 printed SIZES line carries the values")
        ok(0.22 <= s1["held_rows"] / 402.0 <= 0.38, "T7 held-out fraction %.3f in [0.22, 0.38]" % (s1["held_rows"] / 402.0))
        con.close()
        # T8
        with open(rel(BASE_TOML), encoding="utf-8") as f:
            base = f.read()
        pid = draws[0]["pool"]
        t = toml_text("N", 1, pid, base)
        cfg = check_toml("N", 1, pid, t, base)
        ok(cfg["outputDir"] == "experiment_results/e1_split_draws/N_e1sd1" and cfg["reservedPoolFile"] ==
           "experiment_configs/e1_split_draws/reserved_pool_e1sd1.json" and cfg["pool"] == pid, "T8 the three keys by value")
        tq = toml_text("Q", 1, pid, base)
        dq = [a for a, b in zip(t.split("\n"), tq.split("\n")) if a != b]
        ok(all(("e1_split_draws/N_e1sd1" in a) or a.startswith("# E1-SPLIT-DRAWS build") or "embedder" in a for a in dq) and
           sum(1 for a in dq if a.startswith("outputDir")) == 1, "T8 N and Q differ only in outputDir (+ header)")
        ok(refused(lambda: check_toml("N", 1, pid, t.replace("minClusterSize        = 55", "minClusterSize        = 56"), base),
                   "differing body lines"), "T8 a 4th changed line REFUSES")
        ok(refused(lambda: check_toml("N", 1, pid, t.replace("seed          = 42", "seed          = 43"), base),
                   "differing body lines"), "T8 a changed seed REFUSES")
        ok(refused(lambda: check_toml("N", 1, "p0000000000000000", t, base), "pool = "), "T8 a wrong pool REFUSES")
        ok(refused(lambda: check_toml("N", 1, pid, t.replace("seed          = 42", "seeds = [42]"), base), "differing body lines")
           or refused(lambda: check_toml("N", 1, pid, t.replace("seed          = 42", "seeds = [42]"), base), "seeds"),
           "T8 seeds = [...] REFUSES")
        ok(refused(lambda: toml_text("N", 1, pid, base.replace("pool             =", "#pool =")), "lacks key line"),
           "T8 a base without the pool line REFUSES")
        # T9 check_run_dir: an engine-shaped run dir is admitted with its snapshot id; each finding REFUSES
        cb = hashlib.sha1(b"blob %d\x00" % len(t.encode()) + t.encode()).hexdigest()
        rdn = os.path.join(td, "rd_ok")
        fake_run_dir(rdn, "N", 1, draws[0], t)
        got = check_run_dir(rdn, "N", 1, draws[0], cb, nomic_pin="PIN")
        ok(got["snapshot"] == "SNAP_N1" and got["pool_line"] == (draws[0]["pool"], str(gate_prediction(draws[0])), "0"),
           "T9 admitted: snapshot SNAP_N1, [POOL] line (pool, gate, closedByContent 0)")
        cases9 = [("closure line", dict(log_extra="x [SPLIT-CLOSURE] 3 train item(s) ...\n"), "SPLIT-CLOSURE"),
                  ("closedByContent 3", dict(closed=3), "[POOL] line"),
                  ("wrong pool", dict(man_over=dict(reserved_pool_id=P2DCA)), "reserved_pool_id"),
                  ("wrong embedder", dict(man_over=dict(embedding_model="qwen3-embedding:latest")), "embedding_model"),
                  ("test_size off by one", dict(man_over=dict(test_size=len(draws[0]["held"]) + 1)), "test_size"),
                  ("gate off", dict(man_over=dict(gate_size=0)), "gate_size"),
                  ("not completed", dict(man_over=dict(exit_reason="error")), "exit_reason"),
                  ("a shuffle seed", dict(man_over=dict(construction_order_shuffle_seed=1)), "construction_order_shuffle_seed"),
                  ("wrong nomic pin", dict(nomic_pin="OTHER"), "nomic_raw pin"),
                  ("no TRAIN-ONLY line", dict(train_only=False), "TRAIN-ONLY")]
        for i, (what, kw, needle) in enumerate(cases9):
            rdb = os.path.join(td, "rd_bad%d" % i)
            fake_run_dir(rdb, "N", 1, draws[0], t, **kw)
            ok(refused(lambda: check_run_dir(rdb, "N", 1, draws[0], cb, nomic_pin="PIN"), needle), "T9 %s REFUSES" % what)
        rdb = os.path.join(td, "rd_cfg")
        fake_run_dir(rdb, "N", 1, draws[0], t + "\n# x")
        ok(refused(lambda: check_run_dir(rdb, "N", 1, draws[0], cb, nomic_pin="PIN"), "config.toml blob"), "T9 a config blob mismatch REFUSES")
        rdq = os.path.join(td, "rd_q")
        fake_run_dir(rdq, "Q", 1, draws[0], t, man_over=dict(embedding_cache_file="w.db"))
        ok(refused(lambda: check_run_dir(rdq, "Q", 1, draws[0], cb), "explicit embedding cache"), "T9 a Q build with a cache file REFUSES")
        rd2 = os.path.join(td, "rd_2snap")
        fake_run_dir(rd2, "N", 1, draws[0], t, log_extra="x Snapshot ID: OTHER\n")
        ok(refused(lambda: check_run_dir(rd2, "N", 1, draws[0], cb, nomic_pin="PIN"), "Snapshot ID"), "T9 two snapshot ids REFUSE")
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)
    print("%s SELFTEST OK: %d checks" % (TAG, n[0]))
    return 0


# Each mutant: (id, description, old source fragment, new fragment). run_mutants() applies one to a temp copy, runs its selftest
# in a subprocess, and requires a non-zero exit (KILLED).
MUTANTS = [
    ("S-M1", "salt dropped (side_hash with the normaliser version)", "SS.side_hash(SS.stem_key(text), salt)", "SS.side_hash(SS.stem_key(text))"),
    ("S-M2", "held-out = GATE instead of EVAL", "HELD_OUT_SIDE = SS.EVAL", "HELD_OUT_SIDE = SS.GATE"),
    ("S-M3", "sentinel rule: local row id kept", "else UNLINKED_BASE - rid", "else rid"),
    ("S-M4", "closure on exact text only (key + engine-move clauses dropped)", "if cl[\"key_overlap\"] or cl[\"text_overlap\"] or cl[\"engine_moves\"]", "if cl[\"text_overlap\"]"),
    ("S-M5", "pool id over all ids (sentinels hashed)", "pool=pool_guard.compute_pool_id(pool_guard.judgeable(ids))", "pool=pool_guard.compute_pool_id(ids)"),
    ("S-M6", "write not write-once", "        if os.path.exists(p):\n            refuse(\"%s exists: the split files", "        if False:\n            refuse(\"%s exists: the split files"),
    ("S-M7", "forbidden pools ignored", "        if d[\"pool\"] in forbidden:", "        if False:"),
    ("S-M8", "near-copy max -> min", "n += int(((H @ T.T).max(1) >= NEAR_COS).sum())", "n += int(((H @ T.T).min(1) >= NEAR_COS).sum())"),
    ("S-M9", "near-copy >= -> >", "(H @ T.T).max(1) >= NEAR_COS", "(H @ T.T).max(1) > NEAR_COS + 1e-12"),
    ("S-M10", "pool_state: any rows = RECORDED", "    if got != want:\n        refuse(\"CONFLICT", "    if False:\n        refuse(\"CONFLICT"),
    ("S-M11", "TOML: changed-key set not checked", "    if keys != sorted(CHANGED_KEYS):", "    if False:"),
    ("S-M12", "engine closure moves not counted", "moves = sum(1 for r in d[\"train\"] if SS.stem_key(r[\"text\"]) in hk)", "moves = 0"),
    ("S-M13", "blank rows silently dropped", "    if blank:\n        refuse(", "    if False:\n        refuse("),
    ("S-M14", "file compare skipped", "        if got != file_bytes(d[\"ids\"]):", "        if False:"),
    ("S-M16", "run dir: [SPLIT-CLOSURE] line not checked", "    if \"[SPLIT-CLOSURE]\" in log:", "    if False:"),
    ("S-M17", "run dir: closedByContent not checked", "pl[0] != (d[\"pool\"], str(gate), \"0\")", "pl[0][:2] != (d[\"pool\"], str(gate))"),
    ("S-M18", "run dir: TRAIN-ONLY line not required", "    if \"[TRAIN-ONLY] after construction: 0 EVAL texts\" not in log:", "    if False:"),
    ("S-M19", "run dir: test_size not compared", "test_size=len(d[\"held\"]), gate_size=gate, corpus_size", "gate_size=gate, corpus_size"),
    ("S-M15", "domain not title-cased", "return \" \".join((w[:1].upper() + w[1:]) if w[:1].islower() else w for w in re.split(r\"[_-]\", c))", "return c"),
]


def run_mutants(src_path=None, mutants=None, script_label="e1sd_split_draw.py"):
    src_path = src_path or os.path.abspath(__file__)
    mutants = MUTANTS if mutants is None else mutants
    with open(src_path, encoding="utf-8") as f:
        src = f.read()
    killed, rows = 0, []
    td = tempfile.mkdtemp(prefix="e1sd_mut_")
    try:
        for mid, desc, old, new in mutants:
            if src.count(old) < 1:
                rows.append((mid, desc, "NOT-APPLIED"))
                continue
            p = os.path.join(HERE, "_mut_%s_%s" % (mid.replace("-", ""), os.path.basename(src_path)))
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(src.replace(old, new, 1))
            try:
                r = subprocess.run([sys.executable, p, "--selftest", "--quiet"], capture_output=True, text=True, cwd=ROOT,
                                   env=dict(os.environ))
                st = "KILLED" if r.returncode != 0 else "SURVIVED"
            finally:
                os.remove(p)
            killed += st == "KILLED"
            rows.append((mid, desc, st))
    finally:
        import shutil
        shutil.rmtree(td, ignore_errors=True)
    for mid, desc, st in rows:
        print("%s MUTANT %-6s %-55s %s" % (TAG, mid, desc, st))
    print("%s MUTANTS: %d of %d KILLED (%s)" % (TAG, killed, len(rows), script_label))
    return 0 if killed == len(rows) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--write", action="store_true")
    g.add_argument("--write-configs", action="store_true")
    g.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--corpus-db", default=None)
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest(quiet=a.quiet)
        if a.mutants:
            return run_mutants()
        if a.write_configs:
            rows, draws = load_draws(data_path(CORPUS_DB, a.corpus_db))
            compare_files(draws)
            write_configs(check_pool_ids(draws, forbidden_pools()))
            return 0
        rows, draws, summ = main_check(a.corpus_db, write=a.write)
        check_configs([d["pool"] for d in draws]) if not a.write else None
        print("%s CHECK OK: 3 splits re-derived, byte-equal, content-closed; pools %s" % (TAG, [d["pool"] for d in draws]))
        return 0
    except Refused:
        return 2


if __name__ == "__main__":
    sys.exit(main())
