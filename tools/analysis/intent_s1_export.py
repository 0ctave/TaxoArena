"""intent_s1_export.py: INTENT-TRANSFER-S1's build-DB exporter, GATE id exports and the nine arm configs. ZERO LLM / judge calls;
no construction, no site null, no pool of record read.

REGISTRATION OF RECORD: docs/judge_v2_program.md, section "## Registered 2026-10-01 (before any code or call) — INTENT-TRANSFER-S1:
on MASSIVE en-US and CLINC150 (gold hierarchies known), ..." (L22682-L22710 _as_of 2daeae31; N1 closed by the bracket in the same
section). What this file implements from it:
  HYGIENE "Build inputs: per-arm build DBs containing TRAIN and GATE rows ONLY (EVAL physically absent from the JVM)", "Split: S0's
    CK-CLOSE-v1 hash sides (EVAL 0.30 / GATE 0.10 / TRAIN 0.60) on intent_transfer_corpora_v1.db (sha256 487e0093...); cross-label
    twins dropped (S0's 22)", "No corpus text in any committed file".
  INSTRUMENT "Arms": M-AF, M-AF', M-o1, M-o2, M-AF-s2, M-AN, C-AF, C-AN, M-AF-g (the nine builds), and "the build-DB exporter,
    TO BE BUILT".
The engine half is DatasetType.INTENT (src/main/kotlin/taxonomy/dataset/MMLUDatasetFetcher.fetchIntent: the build DB is refused
unless every row is TRAIN or GATE and intent_build_meta's counts match; the embedding file must be a per-run intent working copy,
EmbeddingCache.resolveIntentWorkingCopy, read-only for vectors).

WHAT IT WRITES (only with --write-configs / --export; --dry-run writes nothing):
  --write-configs  experiment_configs/intent_s1/gate_ids_<corpus>_s<salt>.json (3 files; {coarse key: sorted engine ids}; ids
                   only, no text), experiment_configs/intent_s1/<slug>.toml (9 arm configs) and
                   experiment_configs/intent_s1/export_manifest.json (pool ids, per-side counts, table shas, ingest sha). WRITE-ONCE
                   per path: an existing path is left alone when byte-identical and REFUSED otherwise.
  --export ARM|all <DATA_ROOT>/intent_s1_build/<slug>.db, created EXCLUSIVELY (an existing file REFUSES), journal DELETE (no -wal
                   left), one per arm (the JVM writes reserved_pool rows into its corpus DB, so arms never share a file). The
                   committed gate export and pool id are re-derived and must equal the committed bytes (REFUSES otherwise).
  DATA_ROOT = TAXOARENA_DATA_ROOT or this checkout. The ingest DB and the pinned intent_emb_<e>.db are opened mode=ro&immutable=1
  after the sidecar check, their sha256 checked against experiment_configs/intent_transfer_s0_pins.json (strict: a null or
  different pin REFUSES) before and after the read.

BUILD DB (schema intent_s1_build/v1; the engine reads it through loadFromDb):
  intent_corpus(id = s, question = text, category = gold COARSE label (MASSIVE scenario / CLINC domain: the anchored arms' anchors;
    the AF arms ignore it), cot_content '', options '[]', answer '', side TRAIN|GATE, fine, n_items);
  eval_question_link(question_id = s, mmlu_pro_row_id = s, ...); corpus_questions(question_id = 11,000,000 + s, text);
  intent_build_meta(schema, corpus, arm, salt, n_train, n_gate, n_items_train, n_items_gate, ingest_db_sha256, table_sha256,
    gate_ids_sha256, pool_id, embedder, script_blob_lf).
  The engine id of a row is 11,000,000 + s (CorpusRegistry: INTENT = (5 + 6) x 1M).

BUILDER'S READINGS (points the registered text leaves open; each printed by --dry-run; the registrar confirms or brackets):
  B1 SALT [SUPERSEDED 2026-10-03 by the ruling bracketed at prog L22688 (L23752-L23758): salt-1 EVAL stays FIXED; salt s >= 2
     re-draws only GATE vs TRAIN among salt-1 non-EVAL items, GATE iff side_hash(stem_key, "norm-v1" U+001F "salt<s>") < 143
     (salted_side); assert_no_eval REFUSES any build row carrying a salt-1 EVAL text or stem key, in derive() and on every
     written DB. The reading below re-hashed all three sides and put 3,456 salt-1 EVAL items into M-AF-s2's build: withdrawn.]
     "a split re-draw salt 2" is not defined in the record. Salt 1 = S0's stored side (re-derived here and asserted equal:
     side_of_hash(side_hash(stem_key))). Salt s >= 2: side_of_hash(side_hash(stem_key, "norm-v1" U+001F "salt<s>")), i.e. the
     normaliser-version field of the hash payload carries the salt; same thresholds, same components (stem_key), same drops.
  B2 ONE ROW PER DISTINCT TEXT. The engine keys a query by its raw text (GraphNode.queryWeights; the anchor-free count guard counts
     distinct texts), so exact duplicates (MASSIVE 59, CLINC 1 among TRAIN+GATE) enter the build once; n_items records the
     multiplicity and the readout maps every item to its text's leaf. Exact duplicates share stem_key, hence side and (cross-label
     components being dropped) both gold labels: asserted.
  B3 s = the 1-based rank of the text among the corpus's DISTINCT kept in-scope texts (every side), ordered by UTF-8 bytes; so an
     item's engine id is the same in every arm and every salt of its corpus.
  B4 CATEGORY = the coarse label for every arm (anchors for M-AN / C-AN; a readout label only under anchorFree).
  B5 ANCHORED-512 = experiment_configs/topic_partition/ng_af_bareq512_s42.toml (the 20NG T1b body: slice 512, bar 0.0145, mcs 55,
     label-free) WITHOUT anchorFree, plus splitDropTopPcs 0 / splitWhiten false as in experiment_configs/promoted/bareq512_s42.toml
     ("bareq512 geometry"); AF-256 = experiment_configs/anchorfree/redraw/af_clean_s42.toml's construction keys (anchorFree, slice
     256 by default, bar 0.025, z 2.0, mcs 55). M-AF-g = M-AF with embeddingSliceDim 768 (EMBED-DIM-SLICE's d_g*, selection.json
     f1b508cf...) and the gemma working copy; its embedding model is a launch property (-Dtaxoadapt.llm.embedding-model), not a key.

LAUNCH (NOT done here; the route of record is E1-ROUTE's working copy, N3: no S1 arm runs before E1-ROUTE is READY and merged).
--launch-plan ARM prints, per arm, the build DB check, the working-copy path <DATA_ROOT>/intent_s1_work/<run id>/intent_emb_<e>.db
and the gradlew bootRun command (-PjvmThreads=12, -Dtaxoarena.embeddingCacheFile=<copy>, -Dtaxoarena.embeddingCacheSourceSha256=<pin>,
-Dtaxoadapt.llm.embedding-model=<tag>, -Dranking.db.path=<run dir>/ratings_intent_s1.db, --args="--config <toml>"). It copies and
launches NOTHING.

  python tools/analysis/intent_s1_export.py --selftest
  python tools/analysis/intent_s1_export.py --mutants
  python tools/analysis/intent_s1_export.py --dry-run                 # counts, pool ids, coverage, B1-B5, config check; writes nothing
  python tools/analysis/intent_s1_export.py --check-configs           # the committed exports / TOMLs equal the regenerated bytes
  python tools/analysis/intent_s1_export.py --export all              # operator, inside the lane (writes the nine build DBs)
  python tools/analysis/intent_s1_export.py --launch-plan M-AF        # prints the route; launches nothing

SELFTEST: 7 cases, 300 value checks on fixtures (no repo DB read): ST-SPLIT (salt 1 = S0's rule re-derived; salt 2 re-draws
~1/2 of keys at EVAL 0.30; a wrong stored side refuses), ST-IDS (B2 / B3 values: counts, UTF-8 ranks, multiplicity, OOS and
cross-label rows absent, salt-invariant ids), ST-EXPORT (the pool-id mirror = IntentDatasetTypeTest.PY_POOL_ID pc8348bc89a58bcc5,
order-free; only GATE ids, namespaced, formatData keys; a key collision and a '/' key refuse), ST-CONFIG (every arm's TOML parsed
by tomllib and its recipe keys asserted; the replay differs by outputDir and its own build DB only), ST-DRY (the real dry_run
entry point on a fixture: 13 planned files, 0 written, coverage and arm lines; write-once; CRLF compares equal), ST-DB (the real
export entry point: nine DBs, 0 EVAL rows, meta = table counts, ids namespaced, same-input arms share the table sha, the salt-2
arm differs; an existing DB and a missing committed config refuse), ST-REFUSE (pin mismatch, null pin, a coverage gap in the LAST
input, a foreign model in a pinned file, the census on EACH corpus (massive TRAIN, clinc GATE; just under 5% passes), a non-empty
-wal, an unknown arm).
SELFTEST MUTANTS (2026-10-02, --mutants: in-process source edits, one at a time; 38 of 38 KILLED): salt 2 = salt 1 | salt-1
stored side not re-derived | EVAL rows enter the build | only TRAIN rows enter the build | dropped rows kept | OOS rows kept |
s ranked over TRAIN+GATE only | s 0-based | duplicates not collapsed | gate export includes TRAIN | gate export without the
namespace | gate export keyed by the raw label | pool id over unsorted lines | pretty keeps underscores | key collision
admitted | AF bar 0.0145 | anchored arm anchor-free | gemma slice dropped | M-o2 seed = 1 | replay shares M-AF's build DB |
labeling on | salt-2 arm uses the salt-1 export | dry run writes configs | write-once off | check-configs ignores differences |
compare without CRLF normalisation | coverage gap admitted | coverage on the first input only | embedding meta unchecked | pin
mismatch admitted | null pin admitted | census unchecked | census min instead of max | build DB overwritten | build DB meta
n_gate from TRAIN | build DB ids without the namespace | export without the config check | export writes the first arm only.
(A first pass left 2 SURVIVING, "pool id over unsorted lines" and "coverage on the first input only"; the order-free pool-id
check and the last-input coverage gap were added.)
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
import split_side as SS            # noqa: E402
import intent_ingest as II         # noqa: E402

TAG = "[INTENT-S1-EXPORT]"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
CONFIG_DIR = os.path.join(ROOT, "experiment_configs", "intent_s1")
PINS_FILE = os.path.join(ROOT, "experiment_configs", "intent_transfer_s0_pins.json")
BUILD_DIR_NAME = "intent_s1_build"
WORK_DIR_NAME = "intent_s1_work"
OUT_ROOT = "experiment_results/intent_transfer/s1"
SCHEMA = "intent_s1_build/v1"
INTENT_OFFSET = 11_000_000          # CorpusRegistry.BUILTIN: (LEADERBOARD_COUNT 5 + index 6) x 1,000,000
TABLE = "intent_corpus"
CORPORA = ("massive", "clinc")
EMB_FILE = {"qwen3": "intent_emb_qwen3.db", "gemma": "intent_emb_gemma.db"}
EMB_MODEL = {"qwen3": "qwen3-embedding:latest", "gemma": "embeddinggemma:latest"}
PLANNED_TG = {"massive": (9870, 1691), "clinc": (13487, 2333)}       # TRAIN / GATE kept in-scope ITEMS at salt 1 (ingest census)
REGISTRATION = ("docs/judge_v2_program.md L22682-L22710 (_as_of 2daeae31), section \"## Registered 2026-10-01 (before any code or "
                "call) — INTENT-TRANSFER-S1: ...\"")

# slug, registered name, corpus, salt, recipe, embedder, extra keys (key, literal) in file order
ARMS = (
    ("m_af", "M-AF", "massive", 1, "AF", "qwen3", ()),
    ("m_af_replay", "M-AF'", "massive", 1, "AF", "qwen3", ()),
    ("m_o1", "M-o1", "massive", 1, "AF", "qwen3", (("constructionOrderShuffleSeed", "1"),)),
    ("m_o2", "M-o2", "massive", 1, "AF", "qwen3", (("constructionOrderShuffleSeed", "2"),)),
    ("m_af_s2", "M-AF-s2", "massive", 2, "AF", "qwen3", ()),
    ("m_an", "M-AN", "massive", 1, "AN", "qwen3", ()),
    ("c_af", "C-AF", "clinc", 1, "AF", "qwen3", ()),
    ("c_an", "C-AN", "clinc", 1, "AN", "qwen3", ()),
    ("m_af_g", "M-AF-g", "massive", 1, "AF", "gemma", (("embeddingSliceDim", "768"),)),
)
ARM_BY = {a[0]: a for a in ARMS}
ARM_BY.update({a[1]: a for a in ARMS})


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def git_blob_lf(path):
    d = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------------------------------------ split, ids, keys
GATE_SALT_UPPER = 143                # B1 as RULED (prog L22688 bracket): GATE iff the salted hash < 143 of 1,000 (the 1:6 GATE:TRAIN share)


def salted_side(stem_key, salt, salt1_side=None):
    """B1 AS RULED 2026-10-03 (prog L22688 bracket; L23752-L23758): salt 1 = S0's rule. Salt s >= 2 keeps the salt-1 EVAL FIXED
    and re-draws ONLY GATE vs TRAIN among salt-1 non-EVAL items: GATE iff side_hash(stem_key, "norm-v1" U+001F "salt<s>") < 143,
    TRAIN otherwise. `salt1_side` (the item's salt-1 side) is required for s >= 2."""
    if salt == 1:
        return SS.side_of_hash(SS.side_hash(stem_key))
    if not isinstance(salt, int) or salt < 2:
        refuse("salt %r: 1 or an integer >= 2" % (salt,))
    if salt1_side not in (SS.EVAL, SS.GATE, SS.TRAIN):
        refuse("salt %d needs the item's salt-1 side (got %r)" % (salt, salt1_side))
    if salt1_side == SS.EVAL:
        return SS.EVAL
    h = SS.side_hash(stem_key, SS.NORMALISER_VERSION + SS.FIELD_SEP + "salt%d" % salt)
    return SS.GATE if h < GATE_SALT_UPPER else SS.TRAIN


def assert_no_eval(rows, items, corpus, where):
    """HARD REFUSAL (B1 ruling; HYGIENE "EVAL physically absent from the JVM"): no build row or export id may carry the text or
    the stem key of ANY salt-1 EVAL row of the corpus (kept, dropped or OOS)."""
    ev = [r for r in items if r["corpus"] == corpus and r["side"] == SS.EVAL]
    ev_keys = {r["stem_key"] for r in ev}
    ev_texts = {r["text"] for r in ev}
    bad = [r["s"] for r in rows if r["text"] in ev_texts or SS.stem_key(r["text"]) in ev_keys or r["side"] == SS.EVAL]
    if bad:
        refuse("%s: %d build row(s) carry a salt-1 EVAL item of %s (first s %s): EVAL must be physically absent" % (where, len(bad), corpus, bad[:3]))
    return len(ev)


def pretty(raw):
    """MMLUDatasetFetcher.formatData's key: split on '_' and '-', upper-case each word's first letter if lower-case, join by ' '."""
    out = []
    for part in raw.replace("-", "_").split("_"):
        out.append(part[:1].upper() + part[1:] if part[:1].islower() else part)
    return " ".join(out)


def pool_id(ids_by_key):
    """ReservedPool.computePoolId for BARE keys (no '/': canonicalLine is `key:id`)."""
    for k in ids_by_key:
        if "/" in k:
            refuse("a '/' key %r would take canonicalLine's source branch; intent keys are bare" % k)
    canon = "\n".join(sorted("%s:%d" % (k, q) for k, ids in ids_by_key.items() for q in ids))
    return "p" + hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build_rows(items, corpus, salt):
    """-> (rows, info). rows: one dict per DISTINCT text of the corpus's kept in-scope items on TRAIN or GATE at `salt` (B2, B3);
    info: per-side item and text counts (EVAL included, for the census), the stem-key closure check, the salt-1 side re-derivation."""
    kept = [r for r in items if r["corpus"] == corpus and r["drop_reason"] is None and not r["is_oos"]]
    if not kept:
        refuse("corpus %s has no kept in-scope item" % corpus)
    for r in kept:
        if r["stem_key"] != SS.stem_key(r["text"]):
            refuse("%s: stored stem_key differs from split_side.stem_key(text)" % r["item_id"])
    mismatch = 0
    if salt == 1:
        mismatch = sum(1 for r in kept if r["side"] != salted_side(r["stem_key"], 1))
        if mismatch:
            refuse("%s: %d kept items' stored side differs from the re-derived salt-1 side" % (corpus, mismatch))
    by_text = {}
    moves = {}
    for r in kept:
        side = r["side"] if salt == 1 else salted_side(r["stem_key"], salt, r["side"])
        moves["%s->%s" % (r["side"], side)] = moves.get("%s->%s" % (r["side"], side), 0) + 1
        g = by_text.setdefault(r["text"], {"side": side, "coarse": r["coarse"], "fine": r["fine"], "stem": r["stem_key"], "items": []})
        if (g["side"], g["coarse"], g["fine"]) != (side, r["coarse"], r["fine"]):
            refuse("%s: exact duplicate texts disagree on side or gold (%s)" % (corpus, r["item_id"]))
        g["items"].append(r["item_id"])
    texts = sorted(by_text, key=lambda t: t.encode("utf-8"))
    if len(texts) >= 1_000_000:
        refuse("%s: %d distinct texts overflow the 1,000,000-wide namespace" % (corpus, len(texts)))
    rows, keys = [], {SS.TRAIN: set(), SS.GATE: set(), SS.EVAL: set()}
    n_items = {SS.TRAIN: 0, SS.GATE: 0, SS.EVAL: 0}
    n_texts = {SS.TRAIN: 0, SS.GATE: 0, SS.EVAL: 0}
    for s, t in enumerate(texts, start=1):
        g = by_text[t]
        n_items[g["side"]] += len(g["items"])
        n_texts[g["side"]] += 1
        keys[g["side"]].add(g["stem"])
        if g["side"] in (SS.TRAIN, SS.GATE):
            rows.append({"s": s, "text": t, "coarse": g["coarse"], "fine": g["fine"], "side": g["side"], "n_items": len(g["items"])})
    clash = (keys[SS.TRAIN] & keys[SS.GATE]) | (keys[SS.TRAIN] & keys[SS.EVAL]) | (keys[SS.GATE] & keys[SS.EVAL])
    if clash:
        refuse("%s salt %d: %d stem keys on two sides (CK-CLOSE-v1 broken)" % (corpus, salt, len(clash)))
    if any(r["side"] == SS.EVAL for r in rows):
        refuse("an EVAL row reached the build rows")
    info = {"n_items": n_items, "n_texts": n_texts, "closure_clash": 0, "salt1_side_mismatch": mismatch, "moves": moves,
            "coarse_labels": len({r["coarse"] for r in kept}), "fine_labels": len({r["fine"] for r in kept})}
    return rows, info


def gate_export(rows):
    """{pretty(coarse): sorted engine ids of the GATE rows}; REFUSES two raw labels that format to one key."""
    raw_of = {}
    for r in rows:
        k = pretty(r["coarse"])
        if raw_of.setdefault(k, r["coarse"]) != r["coarse"]:
            refuse("coarse labels %r and %r format to one engine key %r" % (raw_of[k], r["coarse"], k))
    out = {}
    for r in rows:
        if r["side"] == SS.GATE:
            out.setdefault(pretty(r["coarse"]), []).append(INTENT_OFFSET + r["s"])
    return {k: sorted(v) for k, v in sorted(out.items())}


def gate_bytes(export):
    return (json.dumps(export, indent=2, sort_keys=True) + "\n").encode("utf-8")


def table_sha(rows):
    h = hashlib.sha256()
    for r in rows:
        h.update((repr((r["s"], r["text"], r["coarse"], r["fine"], r["side"], r["n_items"])) + "\n").encode("utf-8"))
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ configs
AF_BODY = """anchorFree = true

runPipeline        = true
runBenchmark       = false
runTrickle         = true
runBaselines       = false
enableFinalMetrics = false
enableLabeling     = false
judgeInduction     = false

dagMode = "DAG_MAX"

maxDepth              = 8
minClusterSize        = 55
proposalSeparationBar = 0.025
tau                   = 1e-6
acceptanceZ           = 2.0
enableRefitGate       = false
"""

AN_BODY = """embeddingSliceDim = 512
splitDropTopPcs   = 0
splitWhiten       = false

runPipeline        = true
runBenchmark       = false
runTrickle         = true
runBaselines       = false
enableFinalMetrics = false
enableLabeling     = false
judgeInduction     = false

dagMode = "DAG_MAX"

maxDepth              = 8
minClusterSize        = 55
proposalSeparationBar = 0.0145
tau                   = 1e-6
acceptanceZ           = 2.0
enableRefitGate       = false
"""

COMMON_TAIL = """
membershipFloor       = 0.25
routingBeamGamma      = 0.2
descentMargin         = 0.12

effectiveSupportFloor = 2.0
defaultKappaPrior     = 10.0

numIterations         = 50
maxLeafAssignments    = 5

fusionSimilarityThreshold = 0.90
enableGtWarmStart         = false

enableProfiling           = true
"""

RECIPE_TEXT = {
    "AF": "AF-256 = experiment_configs/anchorfree/redraw/af_clean_s42.toml's construction keys (label-free, anchorFree, slice 256 by"
          " default, bar 0.025, z 2.0, mcs 55)",
    "AN": "anchored-512 = experiment_configs/topic_partition/ng_af_bareq512_s42.toml without anchorFree, plus splitDropTopPcs 0 /"
          " splitWhiten false (bareq512 geometry: slice 512, bar 0.0145, mcs 55; label-free); anchors = the gold coarse labels",
}


def gate_file_rel(corpus, salt):
    return "experiment_configs/intent_s1/gate_ids_%s_s%d.json" % (corpus, salt)


def toml_text(arm, pid):
    slug, name, corpus, salt, recipe, emb, extra = arm
    lines = [
        "# INTENT-TRANSFER-S1 arm %s (%s). %s." % (name, slug, REGISTRATION),
        "# ZERO judge / LLM calls; label-free; no site null. GENERATED by tools/analysis/intent_s1_export.py --write-configs (write-once;",
        "# --check-configs re-derives these bytes). Recipe: %s." % RECIPE_TEXT[recipe],
        "# Corpus %s, split salt %d (builder's reading B1), embedder %s (%s, RAW) through a per-run WORKING COPY of the pinned"
        % (corpus, salt, emb, EMB_MODEL[emb]),
        "# %s (-Dtaxoarena.embeddingCacheFile; DatasetType.INTENT refuses any other route). Build DB = TRAIN + GATE rows only"
        % EMB_FILE[emb],
        "# (intent_s1_export.py --export); reservedPoolFile = its GATE export, pool = that export's id ([POOL-PIN]); testRatio is ignored",
        "# under reservedPoolFile. Own ratings DB: -Dranking.db.path=<run dir>/ratings_intent_s1.db. No `seeds = [...]`.",
    ]
    if extra:
        lines.append("# Arm-specific key(s) beyond the recipe: %s." % ", ".join("%s = %s" % kv for kv in extra))
    if emb != "qwen3":
        lines.append("# Launch property: -Dtaxoadapt.llm.embedding-model=%s (secondary arm; run only after E1-ROUTE is READY and merged)."
                     % EMB_MODEL[emb])
    lines += [
        "#",
        'datasetType   = "INTENT"',
        'corpusDbPath  = "%s/%s.db"' % (BUILD_DIR_NAME, slug),
        "",
        "models        = []",
        "",
        'category      = ""',
        "queryLimit    = 0",
        'outputDir     = "%s/%s"' % (OUT_ROOT, slug),
        "testRatio     = 0.3",
        "seed          = 42",
        "",
        'reservedPoolFile = "%s"' % gate_file_rel(corpus, salt),
        'pool             = "%s"' % pid,
        "",
    ]
    body = (AF_BODY if recipe == "AF" else AN_BODY).rstrip("\n") + "\n"
    if extra:
        body += "\n" + "".join("%s = %s\n" % kv for kv in extra)
    return ("\n".join(lines) + "\n" + body + COMMON_TAIL).encode("utf-8")


# ------------------------------------------------------------------------------------------------ inputs
def pin_of(key, sub=None, pins_file=None):
    pins = II.load_pins(pins_file or PINS_FILE)
    return pins.get(key) if sub is None else (pins.get(key) or {}).get(sub)


def checked_sha(path, want, label):
    """sha256 of a DB file after the sidecar check; REFUSES a null or different pin."""
    II.open_db_ro(path).close()
    s = II.file_sha(path)
    print("%s pin %s: sha256 %s [%s]" % (TAG, label, s, "UNPINNED" if not want else ("PIN OK" if want == s else "PIN MISMATCH")))
    if not want:
        refuse("%s is UNPINNED in %s" % (label, PINS_FILE))
    if want != s:
        refuse("%s sha256 %s != the pinned %s" % (label, s, want))
    return s


def load_items(db, want_sha):
    s0 = checked_sha(db, want_sha, os.path.basename(db))
    con = II.open_db_ro(db)
    try:
        rows = II.rows_from_db(con)
    finally:
        con.close()
    if II.file_sha(db) != s0:
        refuse("%s changed during the read" % db)
    return rows, s0


def coverage(emb_db, texts):
    """-> number of `texts` with a vector in the pinned embedding DB (read-only, immutable)."""
    con = II.open_db_ro(emb_db)
    try:
        have = 0
        tl = list(texts)
        for i in range(0, len(tl), 900):
            chunk = tl[i:i + 900]
            q = "SELECT COUNT(*) FROM embeddings WHERE query IN (%s)" % ",".join("?" * len(chunk))
            have += con.execute(q, chunk).fetchone()[0]
        meta = dict(con.execute("SELECT key, value FROM intent_meta").fetchall())
    finally:
        con.close()
    return have, meta


# ------------------------------------------------------------------------------------------------ derivation (shared by every mode)
def derive(items):
    """-> {(corpus, salt): {rows, info, export, pool, table_sha}} for every input the nine arms use."""
    out = {}
    for key in sorted({(a[2], a[3]) for a in ARMS}):
        rows, info = build_rows(items, *key)
        info["eval_items_checked"] = assert_no_eval(rows, items, key[0], "%s salt %d" % key)
        exp = gate_export(rows)
        out[key] = {"rows": rows, "info": info, "export": exp, "pool": pool_id(exp), "table_sha": table_sha(rows),
                    "gate_bytes": gate_bytes(exp)}
    return out


def manifest_obj(D, ingest_sha):
    m = {"schema": "intent_s1_export_manifest/v1", "registration": REGISTRATION, "ingest_db_sha256": ingest_sha,
         "engine_id_offset": INTENT_OFFSET, "inputs": {}, "arms": {}}
    for (c, s), d in sorted(D.items()):
        m["inputs"]["%s_s%d" % (c, s)] = {
            "n_train_rows": sum(1 for r in d["rows"] if r["side"] == SS.TRAIN),
            "n_gate_rows": sum(1 for r in d["rows"] if r["side"] == SS.GATE),
            "n_items": d["info"]["n_items"], "n_texts": d["info"]["n_texts"], "table_sha256": d["table_sha"],
            "gate_file": gate_file_rel(c, s), "gate_ids_sha256": sha256_bytes(d["gate_bytes"]), "pool_id": d["pool"]}
    for a in ARMS:
        m["arms"][a[1]] = {"slug": a[0], "corpus": a[2], "salt": a[3], "recipe": a[4], "embedder": a[5],
                           "config": "experiment_configs/intent_s1/%s.toml" % a[0], "build_db": "%s/%s.db" % (BUILD_DIR_NAME, a[0]),
                           "pool_id": D[(a[2], a[3])]["pool"]}
    return (json.dumps(m, indent=1, sort_keys=True) + "\n").encode("utf-8")


def planned_files(D, ingest_sha, config_dir):
    files = {}
    for (c, s), d in D.items():
        files[os.path.join(config_dir, "gate_ids_%s_s%d.json" % (c, s))] = d["gate_bytes"]
    for a in ARMS:
        files[os.path.join(config_dir, "%s.toml" % a[0])] = toml_text(a, D[(a[2], a[3])]["pool"])
    files[os.path.join(config_dir, "export_manifest.json")] = manifest_obj(D, ingest_sha)
    return files


def compare_files(files):
    """-> (same, differ, absent) lists of paths (committed bytes compared after CRLF -> LF)."""
    same, differ, absent = [], [], []
    for p, b in sorted(files.items()):
        if not os.path.exists(p):
            absent.append(p)
        elif open(p, "rb").read().replace(b"\r\n", b"\n") == b:
            same.append(p)
        else:
            differ.append(p)
    return same, differ, absent


def write_configs(D, ingest_sha, config_dir):
    files = planned_files(D, ingest_sha, config_dir)
    same, differ, absent = compare_files(files)
    if differ:
        refuse("write-once: %d committed file(s) differ from the regenerated bytes: %s" % (len(differ), [os.path.basename(p) for p in differ]))
    os.makedirs(config_dir, exist_ok=True)
    for p in absent:
        with open(p, "xb") as f:
            f.write(files[p])
    print("%s configs: %d written, %d already identical, 0 differ (%s)" % (TAG, len(absent), len(same), config_dir))
    return files


# ------------------------------------------------------------------------------------------------ the build DB
BUILD_SCHEMA = """
CREATE TABLE intent_corpus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    cot_content TEXT,
    options TEXT,
    answer TEXT,
    side TEXT NOT NULL CHECK (side IN ('TRAIN', 'GATE')),
    fine TEXT NOT NULL,
    n_items INTEGER NOT NULL
);
CREATE TABLE eval_question_link (
    question_id      INTEGER PRIMARY KEY,
    mmlu_pro_row_id  INTEGER,
    question_text    TEXT,
    has_embedding    INTEGER DEFAULT 0
);
CREATE TABLE corpus_questions (
    question_id INTEGER PRIMARY KEY,
    text TEXT
);
CREATE TABLE intent_build_meta (key TEXT PRIMARY KEY, value TEXT);
"""


def build_meta(arm, d, ingest_sha):
    slug, name, corpus, salt, recipe, emb, _ = arm
    rows = d["rows"]
    return {
        "schema": SCHEMA, "corpus": corpus, "arm": name, "slug": slug, "salt": str(salt), "recipe": recipe, "embedder": emb,
        "n_train": str(sum(1 for r in rows if r["side"] == SS.TRAIN)),
        "n_gate": str(sum(1 for r in rows if r["side"] == SS.GATE)),
        "n_items_train": str(sum(r["n_items"] for r in rows if r["side"] == SS.TRAIN)),
        "n_items_gate": str(sum(r["n_items"] for r in rows if r["side"] == SS.GATE)),
        "ingest_db_sha256": ingest_sha, "table_sha256": d["table_sha"], "gate_ids_sha256": sha256_bytes(d["gate_bytes"]),
        "pool_id": d["pool"], "script_blob_lf": git_blob_lf(os.path.abspath(__file__)),
    }


def write_build_db(path, arm, d, ingest_sha):
    if os.path.lexists(path):
        refuse("%s exists: a build DB is written once (a fresh file per arm)" % path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "xb").close()                     # exclusive create: a racing writer refuses here
    con = sqlite3.connect(path)
    try:
        con.execute("PRAGMA journal_mode=DELETE")
        con.executescript(BUILD_SCHEMA)
        for r in d["rows"]:
            con.execute("INSERT INTO intent_corpus (id, question, category, cot_content, options, answer, side, fine, n_items)"
                        " VALUES (?,?,?,'','[]','',?,?,?)", (r["s"], r["text"], r["coarse"], r["side"], r["fine"], r["n_items"]))
            con.execute("INSERT INTO eval_question_link (question_id, mmlu_pro_row_id, question_text, has_embedding) VALUES (?,?,?,0)",
                        (r["s"], r["s"], r["text"]))
            con.execute("INSERT INTO corpus_questions (question_id, text) VALUES (?,?)", (INTENT_OFFSET + r["s"], r["text"]))
        for k, v in build_meta(arm, d, ingest_sha).items():
            con.execute("INSERT INTO intent_build_meta VALUES (?,?)", (k, v))
        con.commit()
    finally:
        con.close()
    return verify_build_db(path, arm, d)


def verify_build_db(path, arm, d):
    """Re-reads a build DB (read-only): 0 EVAL rows, the table re-hashes to the derivation's sha, meta counts agree."""
    con = II.open_db_ro(path)
    try:
        bad = con.execute("SELECT COUNT(*) FROM %s WHERE side NOT IN ('TRAIN','GATE')" % TABLE).fetchone()[0]
        rows = [{"s": s, "text": t, "coarse": c, "fine": f, "side": sd, "n_items": n} for s, t, c, f, sd, n in
                con.execute("SELECT id, question, category, fine, side, n_items FROM %s ORDER BY id" % TABLE)]
        meta = dict(con.execute("SELECT key, value FROM intent_build_meta").fetchall())
    finally:
        con.close()
    if bad:
        refuse("%s holds %d non-TRAIN/GATE rows" % (path, bad))
    if table_sha(rows) != d["table_sha"]:
        refuse("%s: table re-hash differs from the derivation" % path)
    if meta.get("arm") != arm[1] or meta.get("pool_id") != d["pool"]:
        refuse("%s: meta arm / pool differ" % path)
    return {"rows": len(rows), "table_sha": d["table_sha"], "file_sha256": II.file_sha(path), "_rows": rows}


# ------------------------------------------------------------------------------------------------ modes
def resolve_arms(spec):
    if spec == "all":
        return list(ARMS)
    if spec not in ARM_BY:
        refuse("unknown arm %r (known: %s)" % (spec, ", ".join(a[1] for a in ARMS)))
    return [ARM_BY[spec]]


def inputs(db=None, pins_file=None):
    db = db or os.path.join(DATA_ROOT, II.DB_NAME)
    items, ingest_sha = load_items(db, pin_of("ingest_db", pins_file=pins_file))
    return items, ingest_sha, db


def print_derivation(D, out=print):
    for (c, s), d in sorted(D.items()):
        i = d["info"]
        nt = sum(1 for r in d["rows"] if r["side"] == SS.TRAIN)
        ng = sum(1 for r in d["rows"] if r["side"] == SS.GATE)
        out("%s input %s salt %d: build rows %d TRAIN + %d GATE (distinct texts); items TRAIN %d / GATE %d / EVAL %d (EVAL NOT in"
            " the build); texts EVAL %d; stem keys on two sides %d; salt-1 stored-side mismatches %d; coarse %d / fine %d labels;"
            " table sha256 %s; GATE export %d keys, pool %s"
            % (TAG, c, s, nt, ng, i["n_items"][SS.TRAIN], i["n_items"][SS.GATE], i["n_items"][SS.EVAL], i["n_texts"][SS.EVAL],
               i["closure_clash"], i["salt1_side_mismatch"], i["coarse_labels"], i["fine_labels"], d["table_sha"][:16],
               len(d["export"]), d["pool"]))
        if s != 1:
            out("%s   salt-%d moves (items, salt-1 side -> salt-%d side): %s (the B1 ruling records TRAIN->GATE 1,413, GATE->TRAIN"
                " 1,435, TRAIN->TRAIN 8,457 on MASSIVE; EVAL->EVAL only)" % (TAG, s, s, json.dumps(i["moves"], sort_keys=True)))
        if s == 1:
            pt, pg = PLANNED_TG[c]
            off = [abs(i["n_items"][SS.TRAIN] - pt) / pt, abs(i["n_items"][SS.GATE] - pg) / pg]
            out("%s   census %s: TRAIN items %d vs planned %d, GATE %d vs %d (max off %.2f%%; > 5%% REFUSES)"
                % (TAG, c, i["n_items"][SS.TRAIN], pt, i["n_items"][SS.GATE], pg, 100 * max(off)))
            if max(off) > 0.05:
                refuse("census %s off by %.2f%% (> 5%%): re-state by bracket before any build" % (c, 100 * max(off)))


def dry_run(db=None, pins_file=None, emb_dir=None, config_dir=None, out=print):
    out("%s DRY RUN: nothing is written, copied or launched; zero calls. %s" % (TAG, REGISTRATION))
    out("%s builder's readings B1-B5 (module docstring): B1 (as ruled) salt s>=2 keeps salt-1 EVAL, GATE iff hash('norm-v1' U+001F 'salt<s>') < 143 among non-EVAL; B2 one build row per"
        " distinct text; B3 s = rank of the text (UTF-8 order) among the corpus's distinct kept in-scope texts; B4 category ="
        " coarse; B5 recipe bodies" % TAG)
    items, ingest_sha, db = inputs(db, pins_file)
    D = derive(items)
    print_derivation(D, out)
    emb_dir = emb_dir or DATA_ROOT
    cov = {}
    for emb in sorted({a[5] for a in ARMS}):
        path = os.path.join(emb_dir, EMB_FILE[emb])
        checked_sha(path, pin_of("emb", emb, pins_file), EMB_FILE[emb])
        texts = {r["text"] for (c, s), d in D.items() if any(a[5] == emb and (a[2], a[3]) == (c, s) for a in ARMS) for r in d["rows"]}
        have, meta = coverage(path, texts)
        cov[emb] = (have, len(texts))
        out("%s coverage %s: %d of %d build texts have a vector (model %s, protocol %s, native dim %s)"
            % (TAG, EMB_FILE[emb], have, len(texts), meta.get("model"), meta.get("protocol"), meta.get("native_dim")))
        if have != len(texts):
            refuse("%s lacks %d build texts: the JVM never embeds under INTENT (the build would refuse)" % (EMB_FILE[emb], len(texts) - have))
        if meta.get("model") != EMB_MODEL[emb] or meta.get("protocol") != "RAW":
            refuse("%s intent_meta model/protocol %r/%r != %r/RAW" % (EMB_FILE[emb], meta.get("model"), meta.get("protocol"), EMB_MODEL[emb]))
    if II.file_sha(db) != ingest_sha:
        refuse("the ingest DB changed during the dry run")
    files = planned_files(D, ingest_sha, config_dir or CONFIG_DIR)
    same, differ, absent = compare_files(files)
    out("%s configs: %d identical to the committed bytes, %d differ, %d absent" % (TAG, len(same), len(differ), len(absent)))
    for a in ARMS:
        d = D[(a[2], a[3])]
        out("%s arm %-8s %-12s corpus %-7s salt %d recipe %s embedder %-5s build rows %5d (TRAIN %5d / GATE %4d) pool %s config %s"
            % (TAG, a[1], a[0], a[2], a[3], a[4], a[5], len(d["rows"]), sum(1 for r in d["rows"] if r["side"] == SS.TRAIN),
               sum(1 for r in d["rows"] if r["side"] == SS.GATE), d["pool"], "OK" if os.path.join(config_dir or CONFIG_DIR, a[0] + ".toml") in same else "NOT COMMITTED/DIFFERS"))
    out("%s DRY RUN complete: %d arms, %d inputs, coverage %s; 0 files written" % (TAG, len(ARMS), len(D),
                                                                               ", ".join("%s %d/%d" % (e, h, n) for e, (h, n) in sorted(cov.items()))))
    return D, files, (same, differ, absent)


def check_configs(db=None, pins_file=None, config_dir=None):
    items, ingest_sha, _ = inputs(db, pins_file)
    D = derive(items)
    same, differ, absent = compare_files(planned_files(D, ingest_sha, config_dir or CONFIG_DIR))
    print("%s check-configs: %d identical, %d differ, %d absent" % (TAG, len(same), len(differ), len(absent)))
    if differ or absent:
        refuse("committed configs differ (%s) or are absent (%s)" % ([os.path.basename(p) for p in differ], [os.path.basename(p) for p in absent]))
    return 0


def export(spec, db=None, pins_file=None, config_dir=None, build_dir=None):
    items, ingest_sha, dbp = inputs(db, pins_file)
    D = derive(items)
    same, differ, absent = compare_files(planned_files(D, ingest_sha, config_dir or CONFIG_DIR))
    if differ or absent:
        refuse("--export needs the committed configs equal to the regenerated bytes (differ %d, absent %d): run --check-configs"
               % (len(differ), len(absent)))
    bdir = build_dir or os.path.join(DATA_ROOT, BUILD_DIR_NAME)
    res = {}
    for a in resolve_arms(spec):
        path = os.path.join(bdir, a[0] + ".db")
        v = write_build_db(path, a, D[(a[2], a[3])], ingest_sha)
        assert_no_eval(v.pop("_rows"), items, a[2], "written %s" % path)          # the B1 hard refusal, on the DB's own rows
        res[a[1]] = v
        print("%s export %s -> %s: %d rows, table sha256 %s, file sha256 %s (EVAL rows 0)" % (TAG, a[1], path, v["rows"], v["table_sha"][:16], v["file_sha256"][:16]))
    if II.file_sha(dbp) != ingest_sha:
        refuse("the ingest DB changed during the export")
    return res


def launch_plan(spec, pins_file=None):
    for a in resolve_arms(spec):
        slug, name, corpus, salt, recipe, emb, _ = a
        pin = pin_of("emb", emb, pins_file)
        print("%s launch plan %s (NOT launched; E1-ROUTE READY and merged first, N3; rule 7 W1-W5; a backup first):" % (TAG, name))
        print("  1. build DB %s/%s/%s.db exists (intent_s1_export.py --export %s) and re-verifies" % (DATA_ROOT, BUILD_DIR_NAME, slug, name))
        print("  2. copy %s/%s (sha256 must be %s) -> %s/%s/<fresh run id>/%s; the copy's sha256 checked = the pin"
              % (DATA_ROOT, EMB_FILE[emb], pin, DATA_ROOT, WORK_DIR_NAME, EMB_FILE[emb]))
        print("  3. gradlew.bat bootRun -PjvmThreads=12 -Dtaxoarena.embeddingCacheFile=<copy> -Dtaxoarena.embeddingCacheSourceSha256=%s"
              " -Dtaxoadapt.llm.embedding-model=%s -Dranking.db.path=<run dir>/ratings_intent_s1.db"
              " --args=\"--config experiment_configs/intent_s1/%s.toml\"" % (pin, EMB_MODEL[emb], slug))
        print("  4. after exit: the pinned %s, the ingest DB, embeddings_cache.db (file + per-table) and snapshots_frozen.db re-hashed"
              " unchanged; the build log shows '[INTENT] fetched' with the build DB's counts" % EMB_FILE[emb])
    return 0


# ------------------------------------------------------------------------------------------------ selftest (fixtures only)
def _fixture_items():
    """Synthetic intent rows (no corpus text): two corpora, a dropped cross-label pair, OOS rows, exact duplicates."""
    rows = []
    k = 0
    for corpus, coarses in (("massive", ("alarm", "smart_home", "iot")), ("clinc", ("banking", "kitchen_and_dining"))):
        for ci, c in enumerate(coarses):
            for fi in range(2):
                fine = "%s_f%d" % (c, fi)
                for j in range(40):
                    text = "synthetic %s utterance %d of %s" % (corpus, j, fine)
                    rows.append({"item_id": "%s:train:%05d" % (corpus, k), "corpus": corpus, "text": text, "coarse": c, "fine": fine,
                                 "is_oos": 0, "drop_reason": None})
                    k += 1
                # an exact duplicate of utterance 0 (same gold): B2 collapses it
                rows.append({"item_id": "%s:train:%05d" % (corpus, k), "corpus": corpus, "text": "synthetic %s utterance 0 of %s" % (corpus, fine),
                             "coarse": c, "fine": fine, "is_oos": 0, "drop_reason": None})
                k += 1
    rows.append({"item_id": "clinc:oos:00001", "corpus": "clinc", "text": "synthetic oos utterance", "coarse": "oos", "fine": "oos",
                 "is_oos": 1, "drop_reason": None})
    rows.append({"item_id": "massive:train:99998", "corpus": "massive", "text": "synthetic twin", "coarse": "alarm", "fine": "alarm_f0",
                 "is_oos": 0, "drop_reason": "cross_label"})
    rows.append({"item_id": "massive:train:99999", "corpus": "massive", "text": "synthetic twin", "coarse": "iot", "fine": "iot_f0",
                 "is_oos": 0, "drop_reason": "cross_label"})
    for r in rows:
        r["stem_key"] = SS.stem_key(r["text"])
        r["hash_side"] = SS.side_of_hash(SS.side_hash(r["stem_key"]))
        r["side"] = SS.EVAL if r["is_oos"] else r["hash_side"]
    return rows


def _write_ingest(path, rows):
    con = sqlite3.connect(path)
    cols = ("item_id", "corpus", "orig_split", "orig_idx", "text", "coarse", "fine", "is_oos", "annot", "stem_key", "hash_side", "side", "drop_reason")
    con.execute("CREATE TABLE items (%s)" % ", ".join(cols))
    for r in rows:
        con.execute("INSERT INTO items VALUES (%s)" % ",".join("?" * len(cols)),
                    tuple(r.get(c, "x" if c in ("orig_split", "orig_idx") else None) for c in cols))
    con.commit()
    con.close()


def _write_emb(path, texts, model):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE intent_meta (key TEXT PRIMARY KEY, value TEXT)")
    for t in texts:
        con.execute("INSERT INTO embeddings VALUES (?, ?)", (t, b"\x00" * 16))
    for k, v in (("model", model), ("protocol", "RAW"), ("native_dim", "4")):
        con.execute("INSERT INTO intent_meta VALUES (?, ?)", (k, v))
    con.commit()
    con.close()


SELFTEST_CASES = ("ST-SPLIT", "ST-IDS", "ST-EXPORT", "ST-CONFIG", "ST-DRY", "ST-DB", "ST-REFUSE")


def selftest(only=None, quiet=False):
    sel = set(only or SELFTEST_CASES)
    ok = [0]

    def check(cond, what):
        if not cond:
            raise AssertionError("SELFTEST FAILED: " + what)
        ok[0] += 1

    def refused(fn, needle):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except SystemExit as e:
            check(needle in str(e), "refusal %r carries %r" % (str(e), needle))
            return
        raise AssertionError("SELFTEST FAILED: expected a refusal containing %r" % needle)

    td = tempfile.mkdtemp(prefix="intent_s1_export_st_")
    items = _fixture_items()
    global PLANNED_TG
    saved_planned = PLANNED_TG
    try:
        if "ST-SPLIT" in sel:
            # salt 1 == S0's rule (re-derived, asserted equal to the stored side); salt 2 differs on some keys, same thresholds
            keys = [SS.stem_key("probe %d" % i) for i in range(2000)]
            s1 = [salted_side(k, 1) for k in keys]
            s2 = [salted_side(k, 2, a) for k, a in zip(keys, s1)]
            check(all(a == SS.side_of_hash(SS.side_hash(k)) for a, k in zip(s1, keys)), "salt 1 is S0's rule")
            check(all((a == SS.EVAL) == (b == SS.EVAL) for a, b in zip(s1, s2)), "B1 ruling: salt 2 keeps the salt-1 EVAL exactly")
            ne = [(a, b) for a, b in zip(s1, s2) if a != SS.EVAL]
            g2 = sum(1 for _, b in ne if b == SS.GATE) / float(len(ne))
            check(0.11 < g2 < 0.18, "salt 2 GATE share among non-EVAL ~ 1/7 (%.3f)" % g2)
            moved = sum(1 for a, b in ne if a != b)
            check(100 < moved < 600, "salt 2 re-draws GATE vs TRAIN (moved %d of %d)" % (moved, len(ne)))
            k0 = next(k for k, a in zip(keys, s1) if a != SS.EVAL)
            h0 = SS.side_hash(k0, "norm-v1\u001fsalt3")
            check(salted_side(k0, 3, SS.TRAIN) == (SS.GATE if h0 < 143 else SS.TRAIN), "salt payload literal and the 143 bar")
            kb = [k for k, a in zip(keys, s1) if a != SS.EVAL and SS.side_hash(k, "norm-v1\u001fsalt2") in (142, 143)]
            for k in kb:
                check(salted_side(k, 2, SS.TRAIN) == (SS.GATE if SS.side_hash(k, "norm-v1\u001fsalt2") == 142 else SS.TRAIN), "the bar is strict < 143")
            refused(lambda: salted_side(keys[0], 0), "salt 0")
            refused(lambda: salted_side(keys[0], 2), "needs the item's salt-1 side")
            # the hard refusal: a build row carrying a salt-1 EVAL text (or stem key) REFUSES
            ev_item = next(r for r in items if r["corpus"] == "massive" and r["side"] == SS.EVAL and r["drop_reason"] is None)
            ok_rows, _ = build_rows(items, "massive", 2)
            check(assert_no_eval(ok_rows, items, "massive", "fixture") > 0, "salt-2 rows carry no EVAL item")
            leak = ok_rows + [{"s": 99999, "text": ev_item["text"], "coarse": "alarm", "fine": "f", "side": SS.TRAIN, "n_items": 1}]
            refused(lambda: assert_no_eval(leak, items, "massive", "fixture"), "carry a salt-1 EVAL item")
            leak2 = ok_rows + [{"s": 99998, "text": "  " + ev_item["text"].upper() + " ", "coarse": "alarm", "fine": "f", "side": SS.GATE, "n_items": 1}]
            refused(lambda: assert_no_eval(leak2, items, "massive", "fixture"), "carry a salt-1 EVAL item")
            ev_drop = next(r for r in items if r["corpus"] == "clinc" and r["is_oos"])
            leak3 = [{"s": 1, "text": ev_drop["text"], "coarse": "banking", "fine": "f", "side": SS.TRAIN, "n_items": 1}]
            refused(lambda: assert_no_eval(leak3, items, "clinc", "fixture"), "carry a salt-1 EVAL item")
            # derive() itself refuses: a (hand-made, inconsistent) dropped EVAL row sharing a kept TRAIN row's text
            tr_item = next(r for r in items if r["corpus"] == "massive" and r["side"] == SS.TRAIN and r["drop_reason"] is None)
            poisoned = items + [dict(tr_item, item_id="massive:train:99997", side=SS.EVAL, drop_reason="cross_label")]
            refused(lambda: derive(poisoned), "carry a salt-1 EVAL item")
            # a stored side that disagrees with the re-derivation REFUSES (salt 1)
            bad = [dict(r) for r in items]
            first = next(r for r in bad if r["corpus"] == "massive" and r["drop_reason"] is None and " utterance 5 of " in r["text"])
            first["side"] = SS.GATE if first["side"] != SS.GATE else SS.TRAIN
            refused(lambda: build_rows(bad, "massive", 1), "stored side differs")
        if "ST-IDS" in sel:
            rows, info = build_rows(items, "massive", 1)
            kept = [r for r in items if r["corpus"] == "massive" and r["drop_reason"] is None and not r["is_oos"]]
            texts = sorted({r["text"] for r in kept}, key=lambda t: t.encode("utf-8"))
            check(info["n_items"][SS.TRAIN] + info["n_items"][SS.GATE] + info["n_items"][SS.EVAL] == len(kept), "every kept item counted once")
            check(sum(info["n_texts"].values()) == len(texts) == len(kept) - 6, "6 exact duplicates collapse (B2): %d" % len(texts))
            check(all(r["side"] in (SS.TRAIN, SS.GATE) for r in rows), "no EVAL row in the build rows")
            check(len(rows) == info["n_texts"][SS.TRAIN] + info["n_texts"][SS.GATE], "rows = TRAIN + GATE texts")
            byt = {r["text"]: r for r in rows}
            for s, t in enumerate(texts, start=1):
                if t in byt:
                    check(byt[t]["s"] == s, "s = UTF-8 rank of the text (B3)")
            dup = [r for r in rows if r["n_items"] == 2]
            check(len(dup) == sum(1 for t in texts if sum(1 for r in kept if r["text"] == t) == 2 and byt.get(t)), "n_items records multiplicity")
            check("synthetic twin" not in byt, "cross-label twins (dropped) never reach the build")
            rows2, info2 = build_rows(items, "massive", 2)
            check({r["s"] for r in rows2} == {r["s"] for r in rows}, "B1 ruling: salt 2 builds on the same non-EVAL texts")
            sd1 = {r["s"]: r["side"] for r in rows}
            check(any(sd1[r["s"]] != r["side"] for r in rows2), "salt 2 moves some rows between GATE and TRAIN")
            check(info2["n_items"][SS.EVAL] == info["n_items"][SS.EVAL], "salt 2: the same EVAL count")
            t2 = {r["text"]: r["s"] for r in rows2}
            check(all(t2[t] == byt[t]["s"] for t in t2 if t in byt), "s is salt-invariant (B3)")
            crows, cinfo = build_rows(items, "clinc", 1)
            check("synthetic oos utterance" not in {r["text"] for r in crows}, "OOS never enters a build")
            ckept = [r for r in items if r["corpus"] == "clinc" and r["drop_reason"] is None and not r["is_oos"]]
            check(sum(cinfo["n_items"].values()) == len(ckept), "clinc: OOS items not counted (%d)" % sum(cinfo["n_items"].values()))
            ctexts = sorted({r["text"] for r in ckept}, key=lambda t: t.encode("utf-8"))
            check(all(r["s"] == ctexts.index(r["text"]) + 1 for r in crows), "clinc: s ranks in-scope texts only (an OOS text shifts no id)")
            check(pretty("smart_home") == "Smart Home" and pretty("iot") == "Iot" and pretty("kitchen_and_dining") == "Kitchen And Dining"
                  and pretty("a-b_c") == "A B C" and pretty("qa") == "Qa", "formatData mirror")
        if "ST-EXPORT" in sel:
            pid = pool_id({"Alarm": [11000002, 11000900], "Smart Home": [11000901]})
            check(pid == "pc8348bc89a58bcc5", "pool id mirror = the Kotlin test's constant (got %s)" % pid)
            check(pool_id({"Smart Home": [11000901], "Alarm": [11000900, 11000002]}) == pid, "pool id is order-free (sorted lines)")
            if not quiet:
                print("%s pool id mirror: %s (IntentDatasetTypeTest.PY_POOL_ID)" % (TAG, pid))
            rows, _ = build_rows(items, "massive", 1)
            exp = gate_export(rows)
            n_gate = sum(1 for r in rows if r["side"] == SS.GATE)
            check(sum(len(v) for v in exp.values()) == n_gate > 0, "every GATE row exported, only GATE rows")
            check(all(INTENT_OFFSET < q < INTENT_OFFSET + 1_000_000 for v in exp.values() for q in v), "ids in the INTENT namespace")
            gate_s = {INTENT_OFFSET + r["s"] for r in rows if r["side"] == SS.GATE}
            check({q for v in exp.values() for q in v} == gate_s, "the export is exactly the GATE ids (none from TRAIN)")
            check(set(exp) <= {"Alarm", "Smart Home", "Iot"}, "keys are formatData keys")
            refused(lambda: pool_id({"MATH/x": [1]}), "'/' key")
            clash = [dict(r) for r in rows] + [{"s": 999, "text": "z", "coarse": "smart-home", "fine": "f", "side": SS.GATE, "n_items": 1}]
            refused(lambda: gate_export(clash), "format to one engine key")
        if "ST-CONFIG" in sel:
            import tomllib
            D = derive(items)
            for a in ARMS:
                t = toml_text(a, D[(a[2], a[3])]["pool"]).decode("utf-8")
                cfg = tomllib.loads(t)
                check(cfg["datasetType"] == "INTENT" and cfg["corpusDbPath"] == "intent_s1_build/%s.db" % a[0], "%s dataset keys" % a[1])
                check(cfg["reservedPoolFile"] == gate_file_rel(a[2], a[3]) and cfg["pool"] == D[(a[2], a[3])]["pool"], "%s split keys" % a[1])
                check(cfg["models"] == [] and cfg["runBenchmark"] is False and cfg["enableLabeling"] is False and cfg["judgeInduction"] is False,
                      "%s zero-call keys" % a[1])
                check(cfg["outputDir"] == "%s/%s" % (OUT_ROOT, a[0]) and "seeds" not in cfg, "%s outputDir / no seeds" % a[1])
                if a[4] == "AF":
                    check(cfg.get("anchorFree") is True and cfg["proposalSeparationBar"] == 0.025 and cfg.get("embeddingSliceDim", 256) ==
                          (768 if a[5] == "gemma" else 256), "%s AF recipe" % a[1])
                else:
                    check("anchorFree" not in cfg and cfg["embeddingSliceDim"] == 512 and cfg["proposalSeparationBar"] == 0.0145
                          and cfg["splitDropTopPcs"] == 0 and cfg["splitWhiten"] is False, "%s anchored recipe" % a[1])
                check(cfg.get("constructionOrderShuffleSeed") == {"M-o1": 1, "M-o2": 2}.get(a[1]), "%s shuffle seed" % a[1])
                check(cfg["minClusterSize"] == 55 and cfg["acceptanceZ"] == 2.0 and cfg["numIterations"] == 50, "%s common keys" % a[1])
            ta = tomllib.loads(toml_text(ARM_BY["M-AF"], "p0").decode())
            tr = tomllib.loads(toml_text(ARM_BY["M-AF'"], "p0").decode())
            check({k for k in ta if ta[k] != tr.get(k)} == {"outputDir", "corpusDbPath"}, "the replay differs by outputDir and its own build DB only")
            check(len({a[0] for a in ARMS}) == 9 and len({toml_text(a, "p0") for a in ARMS}) == 9, "nine distinct arm configs")
        if "ST-DRY" in sel or "ST-DB" in sel or "ST-REFUSE" in sel:
            ing = os.path.join(td, "intent_transfer_corpora_v1.db")
            _write_ingest(ing, items)
            ing_sha = II.file_sha(ing)
            D = derive(items)
            q_texts = {r["text"] for (c, s), d in D.items() for r in d["rows"]}
            g_texts = {r["text"] for r in D[("massive", 1)]["rows"]}
            emb_dir = os.path.join(td, "emb")
            os.makedirs(emb_dir)
            _write_emb(os.path.join(emb_dir, EMB_FILE["qwen3"]), q_texts, EMB_MODEL["qwen3"])
            _write_emb(os.path.join(emb_dir, EMB_FILE["gemma"]), g_texts, EMB_MODEL["gemma"])
            pins = {"schema": II.PINS_SCHEMA, "raw": {}, "ingest_db": ing_sha,
                    "emb": {e: II.file_sha(os.path.join(emb_dir, EMB_FILE[e])) for e in ("qwen3", "gemma")}}
            pins["emb"]["nomic"] = None
            pf = os.path.join(td, "pins.json")
            open(pf, "w").write(json.dumps(pins))
            cdir = os.path.join(td, "cfg")
            PLANNED_TG = {c: (D[(c, 1)]["info"]["n_items"][SS.TRAIN], D[(c, 1)]["info"]["n_items"][SS.GATE]) for c in CORPORA}
        if "ST-DRY" in sel:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                Dd, files, (same, differ, absent) = dry_run(db=ing, pins_file=pf, emb_dir=emb_dir, config_dir=cdir, out=print)
            txt = buf.getvalue()
            check(not os.path.exists(cdir), "the dry run writes no config")
            check(len(absent) == len(files) == 13 and not same and not differ, "dry run: 13 planned files, all absent")
            check("0 files written" in txt and "coverage intent_emb_qwen3.db: %d of %d" % (len(q_texts), len(q_texts)) in txt, "dry run coverage line")
            for a in ARMS:
                check(("arm %-8s %-12s" % (a[1], a[0])) in txt and Dd[(a[2], a[3])]["pool"] in txt, "dry run prints arm %s and its pool" % a[1])
            check(txt.count("PIN OK") == 3, "three pins checked (ingest, qwen3, gemma)")
            # write, then check: identical -> 0 written; a hand-edited file -> REFUSED (write-once)
            with contextlib.redirect_stdout(io.StringIO()):
                write_configs(Dd, ing_sha, cdir)
            check(len(os.listdir(cdir)) == 13, "13 files written")
            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                write_configs(Dd, ing_sha, cdir)
            check("0 written, 13 already identical" in buf2.getvalue(), "re-write is a no-op on identical bytes")
            with contextlib.redirect_stdout(io.StringIO()):
                check(check_configs(db=ing, pins_file=pf, config_dir=cdir) == 0, "check-configs passes on identical bytes")
            p = os.path.join(cdir, "m_af.toml")
            orig = open(p, "rb").read()
            open(p, "wb").write(orig.replace(b"proposalSeparationBar = 0.025", b"proposalSeparationBar = 0.026"))
            refused(lambda: write_configs(Dd, ing_sha, cdir), "write-once")
            refused(lambda: check_configs(db=ing, pins_file=pf, config_dir=cdir), "committed configs differ")
            open(p, "wb").write(orig.replace(b"\n", b"\r\n"))
            with contextlib.redirect_stdout(io.StringIO()):
                check(check_configs(db=ing, pins_file=pf, config_dir=cdir) == 0, "a CRLF checkout compares equal (LF of record)")
            open(p, "wb").write(orig)
        if "ST-DB" in sel:
            cdir2 = os.path.join(td, "cfg2")
            with contextlib.redirect_stdout(io.StringIO()):
                write_configs(D, ing_sha, cdir2)
            bdir = os.path.join(td, "build")
            with contextlib.redirect_stdout(io.StringIO()):
                res = export("all", db=ing, pins_file=pf, config_dir=cdir2, build_dir=bdir)
            check(len(res) == 9 and len(os.listdir(bdir)) == 9, "nine build DBs, one per arm")
            check(not any(f.endswith(("-wal", "-journal", "-shm")) for f in os.listdir(bdir)), "no sidecar left")
            con = sqlite3.connect(os.path.join(bdir, "m_af.db"))
            n_eval = con.execute("SELECT COUNT(*) FROM intent_corpus WHERE side NOT IN ('TRAIN','GATE')").fetchone()[0]
            meta = dict(con.execute("SELECT key, value FROM intent_build_meta").fetchall())
            nt = con.execute("SELECT COUNT(*) FROM intent_corpus WHERE side='TRAIN'").fetchone()[0]
            ng = con.execute("SELECT COUNT(*) FROM intent_corpus WHERE side='GATE'").fetchone()[0]
            ids = [r[0] for r in con.execute("SELECT question_id FROM corpus_questions ORDER BY question_id")]
            link = con.execute("SELECT COUNT(*) FROM eval_question_link l JOIN intent_corpus m ON m.id = l.mmlu_pro_row_id"
                               " WHERE l.question_id = m.id").fetchone()[0]
            con.close()
            check(n_eval == 0, "0 EVAL rows in the build DB")
            check(meta["schema"] == SCHEMA and meta["n_train"] == str(nt) and meta["n_gate"] == str(ng), "meta counts = table counts")
            check(meta["arm"] == "M-AF" and meta["salt"] == "1" and meta["pool_id"] == D[("massive", 1)]["pool"], "meta arm / salt / pool")
            check(all(INTENT_OFFSET < q < INTENT_OFFSET + 1_000_000 for q in ids) and link == nt + ng, "ids namespaced; every row linked")
            rs = res["M-AF"]["table_sha"] == res["M-AF'"]["table_sha"] == res["M-AN"]["table_sha"] != res["M-AF-s2"]["table_sha"]
            check(rs, "same-input arms share the table sha; the salt-2 arm differs")
            con = sqlite3.connect(os.path.join(bdir, "m_af_s2.db"))
            check(con.execute("SELECT value FROM intent_build_meta WHERE key='salt'").fetchone()[0] == "2", "salt-2 meta")
            con.close()
            refused(lambda: export("M-AF", db=ing, pins_file=pf, config_dir=cdir2, build_dir=bdir), "is written once")
            os.remove(os.path.join(cdir2, "c_an.toml"))
            refused(lambda: export("C-AF", db=ing, pins_file=pf, config_dir=cdir2, build_dir=os.path.join(td, "build_b")), "--export needs the committed configs")
        if "ST-REFUSE" in sel:
            bad_pins = dict(pins, ingest_db="0" * 64)
            pf2 = os.path.join(td, "pins_bad.json")
            open(pf2, "w").write(json.dumps(bad_pins))
            refused(lambda: dry_run(db=ing, pins_file=pf2, emb_dir=emb_dir, config_dir=cdir), "!= the pinned")
            null_pins = dict(pins, emb={"qwen3": pins["emb"]["qwen3"], "gemma": None})
            pf3 = os.path.join(td, "pins_null.json")
            open(pf3, "w").write(json.dumps(null_pins))
            refused(lambda: dry_run(db=ing, pins_file=pf3, emb_dir=emb_dir, config_dir=cdir), "UNPINNED")
            # a missing build text in an embedding DB REFUSES (the JVM never embeds under INTENT)
            emb2 = os.path.join(td, "emb2")
            os.makedirs(emb2)
            m_only = sorted({r["text"] for r in D[("massive", 2)]["rows"]} - {r["text"] for r in D[("clinc", 1)]["rows"]})
            check(len(m_only) > 0, "a MASSIVE text absent from the first input (CLINC)")
            _write_emb(os.path.join(emb2, EMB_FILE["qwen3"]), sorted(q_texts - {m_only[0]}), EMB_MODEL["qwen3"])     # not the FIRST input's text
            _write_emb(os.path.join(emb2, EMB_FILE["gemma"]), g_texts, EMB_MODEL["gemma"])
            pins4 = dict(pins, emb={e: II.file_sha(os.path.join(emb2, EMB_FILE[e])) for e in ("qwen3", "gemma")})
            pf4 = os.path.join(td, "pins4.json")
            open(pf4, "w").write(json.dumps(pins4))
            refused(lambda: dry_run(db=ing, pins_file=pf4, emb_dir=emb2, config_dir=cdir), "lacks 1 build texts")
            # a gemma file whose meta names another model REFUSES
            emb3 = os.path.join(td, "emb3")
            os.makedirs(emb3)
            _write_emb(os.path.join(emb3, EMB_FILE["qwen3"]), q_texts, EMB_MODEL["qwen3"])
            _write_emb(os.path.join(emb3, EMB_FILE["gemma"]), g_texts, "nomic-embed-text:latest")
            pins5 = dict(pins, emb={e: II.file_sha(os.path.join(emb3, EMB_FILE[e])) for e in ("qwen3", "gemma")})
            pf5 = os.path.join(td, "pins5.json")
            open(pf5, "w").write(json.dumps(pins5))
            refused(lambda: dry_run(db=ing, pins_file=pf5, emb_dir=emb3, config_dir=cdir), "intent_meta model/protocol")
            # census > 5% REFUSES (planned counts moved 6%)
            base = {c: (D[(c, 1)]["info"]["n_items"][SS.TRAIN], D[(c, 1)]["info"]["n_items"][SS.GATE]) for c in CORPORA}
            PLANNED_TG = dict(base, massive=(int(round(base["massive"][0] * 1.06)), base["massive"][1]))     # massive TRAIN off 6%
            refused(lambda: dry_run(db=ing, pins_file=pf, emb_dir=emb_dir, config_dir=cdir), "census massive off")
            PLANNED_TG = dict(base, clinc=(base["clinc"][0], int(round(base["clinc"][1] * 1.2))))            # clinc GATE off: every site
            refused(lambda: dry_run(db=ing, pins_file=pf, emb_dir=emb_dir, config_dir=cdir), "census clinc off")
            n_m = base["massive"][0]
            PLANNED_TG = dict(base, massive=(int(n_m / 1.049) + 1, base["massive"][1]))                  # just under 5% passes
            with contextlib.redirect_stdout(io.StringIO()):
                dry_run(db=ing, pins_file=pf, emb_dir=emb_dir, config_dir=cdir)
            PLANNED_TG = {c: (D[(c, 1)]["info"]["n_items"][SS.TRAIN], D[(c, 1)]["info"]["n_items"][SS.GATE]) for c in CORPORA}
            # a non-empty -wal beside the ingest DB REFUSES before any read
            open(ing + "-wal", "wb").write(b"x")
            refused(lambda: dry_run(db=ing, pins_file=pf, emb_dir=emb_dir, config_dir=cdir), "-wal is non-empty")
            os.remove(ing + "-wal")
            refused(lambda: resolve_arms("M-XX"), "unknown arm")
    finally:
        PLANNED_TG = saved_planned
        import shutil
        shutil.rmtree(td, ignore_errors=True)
    if not quiet:
        print("%s SELFTEST OK: %d checks (%s)" % (TAG, ok[0], ", ".join(c for c in SELFTEST_CASES if c in sel)))
    return 0


# ------------------------------------------------------------------------------------------------ mutants (source edits; each must fail a selftest)
MUTANTS = (
    ("salt 2 = salt 1 (no re-draw)", "    return SS.GATE if h < GATE_SALT_UPPER else SS.TRAIN\n", "    return salt1_side\n", ("ST-SPLIT",)),
    ("B1 withdrawn reading: salt 2 re-draws EVAL", "    if salt1_side == SS.EVAL:\n        return SS.EVAL\n", "    if False:\n        return SS.EVAL\n", ("ST-SPLIT",)),
    ("salt 2 GATE bar 400", "GATE_SALT_UPPER = 143 ", "GATE_SALT_UPPER = 400 ", ("ST-SPLIT",)),
    ("salt 2 GATE bar <=", "    return SS.GATE if h < GATE_SALT_UPPER else SS.TRAIN\n", "    return SS.GATE if h <= GATE_SALT_UPPER else SS.TRAIN\n", ("ST-SPLIT",)),
    ("no-EVAL check by text only (stem key dropped)", "if r[\"text\"] in ev_texts or SS.stem_key(r[\"text\"]) in ev_keys or r[\"side\"] == SS.EVAL]",
     "if r[\"text\"] in ev_texts or r[\"side\"] == SS.EVAL]", ("ST-SPLIT",)),
    ("no-EVAL check over kept in-scope EVAL only", "    ev = [r for r in items if r[\"corpus\"] == corpus and r[\"side\"] == SS.EVAL]\n",
     "    ev = [r for r in items if r[\"corpus\"] == corpus and r[\"side\"] == SS.EVAL and r[\"drop_reason\"] is None and not r[\"is_oos\"]]\n", ("ST-SPLIT",)),
    ("no-EVAL check not called by derive", "        info[\"eval_items_checked\"] = assert_no_eval(rows, items, key[0], \"%s salt %d\" % key)\n", "", ("ST-SPLIT",)),
    ("salt-1 stored side not re-derived", "        if mismatch:\n            refuse(", "        if False:\n            refuse(", ("ST-SPLIT",)),
    ("EVAL rows enter the build", "        if g[\"side\"] in (SS.TRAIN, SS.GATE):\n", "        if True:\n", ("ST-IDS",)),
    ("only TRAIN rows enter the build (GATE dropped)", "        if g[\"side\"] in (SS.TRAIN, SS.GATE):\n", "        if g[\"side\"] in (SS.TRAIN,):\n", ("ST-IDS",)),
    ("dropped rows kept", "if r[\"corpus\"] == corpus and r[\"drop_reason\"] is None and not r[\"is_oos\"]]",
     "if r[\"corpus\"] == corpus and not r[\"is_oos\"]]", ("ST-IDS",)),
    ("OOS rows kept", "if r[\"corpus\"] == corpus and r[\"drop_reason\"] is None and not r[\"is_oos\"]]",
     "if r[\"corpus\"] == corpus and r[\"drop_reason\"] is None]", ("ST-IDS",)),
    ("s ranked over TRAIN+GATE only (salt-dependent ids)", "    texts = sorted(by_text, key=lambda t: t.encode(\"utf-8\"))\n",
     "    texts = sorted([t for t in by_text if by_text[t][\"side\"] != SS.EVAL], key=lambda t: t.encode(\"utf-8\"))\n", ("ST-IDS",)),
    ("s 0-based", "    for s, t in enumerate(texts, start=1):\n        g = by_text[t]\n", "    for s, t in enumerate(texts, start=0):\n        g = by_text[t]\n", ("ST-IDS",)),
    ("duplicates not collapsed (n_items 1)", "\"side\": g[\"side\"], \"n_items\": len(g[\"items\"])})", "\"side\": g[\"side\"], \"n_items\": 1})", ("ST-IDS",)),
    ("gate export includes TRAIN", "        if r[\"side\"] == SS.GATE:\n            out.setdefault(", "        if r[\"side\"] in (SS.GATE, SS.TRAIN):\n            out.setdefault(", ("ST-EXPORT",)),
    ("gate export without the namespace", "            out.setdefault(pretty(r[\"coarse\"]), []).append(INTENT_OFFSET + r[\"s\"])\n",
     "            out.setdefault(pretty(r[\"coarse\"]), []).append(r[\"s\"])\n", ("ST-EXPORT",)),
    ("gate export keyed by the raw label", "            out.setdefault(pretty(r[\"coarse\"]), []).append(INTENT_OFFSET + r[\"s\"])\n",
     "            out.setdefault(r[\"coarse\"], []).append(INTENT_OFFSET + r[\"s\"])\n", ("ST-EXPORT",)),
    ("pool id over unsorted lines", "    canon = \"\\n\".join(sorted(\"%s:%d\" % (k, q) for k, ids in ids_by_key.items() for q in ids))\n",
     "    canon = \"\\n\".join(\"%s:%d\" % (k, q) for k, ids in ids_by_key.items() for q in ids)\n", ("ST-EXPORT",)),
    ("pretty keeps underscores", "    for part in raw.replace(\"-\", \"_\").split(\"_\"):\n", "    for part in [raw]:\n", ("ST-IDS",)),
    ("key collision admitted", "        if raw_of.setdefault(k, r[\"coarse\"]) != r[\"coarse\"]:\n", "        if False:\n", ("ST-EXPORT",)),
    ("AF bar 0.0145", "proposalSeparationBar = 0.025\ntau", "proposalSeparationBar = 0.0145\ntau", ("ST-CONFIG",)),
    ("anchored arm anchor-free", "AN_BODY = \"\"\"embeddingSliceDim = 512\n", "AN_BODY = \"\"\"anchorFree = true\nembeddingSliceDim = 512\n", ("ST-CONFIG",)),
    ("gemma slice dropped", "    (\"m_af_g\", \"M-AF-g\", \"massive\", 1, \"AF\", \"gemma\", ((\"embeddingSliceDim\", \"768\"),)),\n",
     "    (\"m_af_g\", \"M-AF-g\", \"massive\", 1, \"AF\", \"gemma\", ()),\n", ("ST-CONFIG",)),
    ("M-o2 seed = 1", "((\"constructionOrderShuffleSeed\", \"2\"),)", "((\"constructionOrderShuffleSeed\", \"1\"),)", ("ST-CONFIG",)),
    ("replay shares M-AF's build DB", "        'corpusDbPath  = \"%s/%s.db\"' % (BUILD_DIR_NAME, slug),\n",
     "        'corpusDbPath  = \"%s/%s.db\"' % (BUILD_DIR_NAME, slug.replace(\"_replay\", \"\")),\n", ("ST-CONFIG",)),
    ("labeling on", "enableLabeling     = false\njudgeInduction     = false\n\ndagMode = \"DAG_MAX\"\n\nmaxDepth              = 8\nminClusterSize        = 55\nproposalSeparationBar = 0.025",
     "enableLabeling     = true\njudgeInduction     = false\n\ndagMode = \"DAG_MAX\"\n\nmaxDepth              = 8\nminClusterSize        = 55\nproposalSeparationBar = 0.025", ("ST-CONFIG",)),
    ("salt-2 arm uses the salt-1 export", "        'reservedPoolFile = \"%s\"' % gate_file_rel(corpus, salt),\n",
     "        'reservedPoolFile = \"%s\"' % gate_file_rel(corpus, 1),\n", ("ST-CONFIG",)),
    ("dry run writes configs", "    files = planned_files(D, ingest_sha, config_dir or CONFIG_DIR)\n    same, differ, absent = compare_files(files)\n    out(",
     "    files = write_configs(D, ingest_sha, config_dir or CONFIG_DIR)\n    same, differ, absent = compare_files(files)\n    out(", ("ST-DRY",)),
    ("write-once off (differing file overwritten)", "    if differ:\n        refuse(\"write-once", "    absent = absent + differ\n    if False:\n        refuse(\"write-once", ("ST-DRY",)),
    ("check-configs ignores differences", "    if differ or absent:\n        refuse(\"committed configs", "    if False:\n        refuse(\"committed configs", ("ST-DRY",)),
    ("compare without CRLF normalisation", "        elif open(p, \"rb\").read().replace(b\"\\r\\n\", b\"\\n\") == b:\n", "        elif open(p, \"rb\").read() == b:\n", ("ST-DRY",)),
    ("coverage gap admitted", "        if have != len(texts):\n", "        if False:\n", ("ST-REFUSE",)),
    ("coverage on the first input only", "        texts = {r[\"text\"] for (c, s), d in D.items() if any(", "        texts = {r[\"text\"] for (c, s), d in list(D.items())[:1] if any(", ("ST-REFUSE",)),
    ("embedding meta unchecked", "        if meta.get(\"model\") != EMB_MODEL[emb] or meta.get(\"protocol\") != \"RAW\":\n", "        if False:\n", ("ST-REFUSE",)),
    ("pin mismatch admitted", "    if want != s:\n        refuse(", "    if False:\n        refuse(", ("ST-REFUSE",)),
    ("null pin admitted", "    if not want:\n        refuse(\"%s is UNPINNED", "    if False:\n        refuse(\"%s is UNPINNED", ("ST-REFUSE",)),
    ("census unchecked", "            if max(off) > 0.05:\n", "            if False:\n", ("ST-REFUSE",)),
    ("census min instead of max", "            if max(off) > 0.05:\n", "            if min(off) > 0.05:\n", ("ST-REFUSE",)),
    ("build DB overwritten", "    if os.path.lexists(path):\n        refuse(\"%s exists: a build DB", "    if False:\n        refuse(\"%s exists: a build DB", ("ST-DB",)),
    ("build DB meta n_gate from TRAIN", "        \"n_gate\": str(sum(1 for r in rows if r[\"side\"] == SS.GATE)),\n",
     "        \"n_gate\": str(sum(1 for r in rows if r[\"side\"] == SS.TRAIN)),\n", ("ST-DB",)),
    ("build DB ids without the namespace", "(INTENT_OFFSET + r[\"s\"], r[\"text\"]))\n", "(r[\"s\"], r[\"text\"]))\n", ("ST-DB",)),
    ("export without the config check", "    if differ or absent:\n        refuse(\"--export needs", "    if False:\n        refuse(\"--export needs", ("ST-DB",)),
    ("export writes the first arm only", "    for a in resolve_arms(spec):\n        path = os.path.join(bdir, a[0] + \".db\")\n",
     "    for a in resolve_arms(spec)[:1]:\n        path = os.path.join(bdir, a[0] + \".db\")\n", ("ST-DB",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read().replace("\r\n", "\n")
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    killed, rows = 0, []
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "intent_s1_export_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new), "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        killed += res.startswith("KILLED")
        rows.append((name, res))
        print("  %-50s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="INTENT-TRANSFER-S1 build-DB exporter and arm configs (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write-configs", action="store_true")
    g.add_argument("--check-configs", action="store_true")
    g.add_argument("--export", metavar="ARM|all")
    g.add_argument("--launch-plan", metavar="ARM|all")
    ap.add_argument("--db", default=None, help="the ingest DB (default DATA_ROOT/intent_transfer_corpora_v1.db)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.dry_run:
        dry_run(db=a.db)
        return 0
    if a.write_configs:
        items, ingest_sha, _ = inputs(a.db)
        write_configs(derive(items), ingest_sha, CONFIG_DIR)
        return 0
    if a.check_configs:
        return check_configs(db=a.db)
    if a.export:
        export(a.export, db=a.db)
        return 0
    return launch_plan(a.launch_plan)


if __name__ == "__main__":
    sys.exit(main())
