"""INTENT-TRANSFER stage 0 ingest (registered: docs/judge_v2_program.md "## Registered 2026-09-29 (before any code or
call) — INTENT-TRANSFER-S0: ...", L22092-L22134 _as_of 44ab46f; the author's D1 "Yes, all three" at L22080-L22090; design
docs/agents/plans/2026-09-29_intent_transfer_design.md, 7a95a1a). ZERO LLM calls; no build; no pool of record read.

What it writes: ONE study DB, `intent_transfer_corpora_v1.db` at DATA_ROOT (the repo root; root `*.db` is gitignored,
.gitignore L58; nothing under experiment_results/, whose *.db are RE-INCLUDED, L145), WRITE-ONCE (refused if it exists),
journal_mode=DELETE (no -wal). Never one of the DBs of record (NEVER_WRITE refused by name). Plus `<db>.manifest.json`
(mode x) under --manifest.

Corpora and their PRIMARY sources (the files the Hugging Face loading scripts of the same corpora download; the URLs are
the builder's, UNVERIFIED by a fetch: the builder was told "no real fetch", and every parser FAILS CLOSED on a layout it
does not recognise, naming what it saw):
  massive    MASSIVE 1.1 en-US (AmazonScience/massive): amazon-massive-dataset-1.1.tar.gz, member */data/en-US.jsonl
             (fields id, locale, partition, scenario, intent, utt, annot_utt); gold coarse = scenario (18), fine = intent (60).
  clinc      CLINC150 "plus" (clinc/clinc_oos, config plus): oos-eval data/data_oos_plus.json (train / val / test /
             oos_train / oos_val / oos_test, each a list of [text, intent]) and data/domains.json (domain -> [intent]);
             gold coarse = domain (10), fine = intent (150), plus the out-of-scope class `oos` (is_oos = 1).
  banking77  BANKING77 (PolyAI/banking77): task-specific-datasets banking_data/train.csv and test.csv (header text,category);
             fine = category (77); no coarse level (coarse NULL).
HWU64 is NOT ingested (D7, the HWU64 <-> MASSIVE-en twin count, is the data-steward's and CONDITIONAL on an author admission, R-3).
The raw files are downloaded ONLY under --fetch, into RAW_DIR (default <HF_HOME or ~/.cache/huggingface>/taxoarena_intent_raw:
inside the Hugging Face cache directory, outside the repo, as the registration's hygiene says; the FILES are the primary ones the
HF loading scripts download, fetched by URL, not the hub's parquet conversions: pyarrow / datasets are not installed, a deviation
the builder reports); a RAW_DIR inside the repo or DATA_ROOT is REFUSED
(`data/**/*.jsonl` is not ignored). Each raw file's sha256 is printed and stored in the DB's provenance table; the
registrar pins them in experiment_configs/intent_transfer_s0_pins.json ("raw"); a pinned file whose sha256 differs REFUSES.

Split (CK-CLOSE-v1 by construction; design section 5): stem_key = split_side.stem_key(text) (norm-v1, options-free);
hash_side = split_side.side_of_hash(split_side.side_hash(stem_key)) (EVAL 0.30 / GATE 0.10 / TRAIN 0.60). Exact norm-v1
duplicates share the key and therefore the side (component = (corpus, stem_key)). side = hash_side, EXCEPT every OOS row:
side = EVAL (design S0-C2: "All OOS rows go to EVAL (never fitted)"), hash_side kept beside it. A component whose rows carry
two gold fine labels (the `oos` class counts as a label) is DROPPED from every readout: drop_reason 'oos_collision' when it
mixes `oos` with an in-scope intent (design: "any OOS row whose stem_key collides with an in-scope row is dropped"; the whole
component goes), 'cross_label' otherwise; an empty norm-v1 text is 'empty'. A NUL byte REFUSES (never repaired).
Cross-corpus stem_key collisions are COUNTED (disclosure; each corpus is read on its own). The split word is the
steward's to grant (S3): nothing here writes "clean", "disjoint" or "held-out".

Schema:
  items(item_id TEXT PK, corpus, orig_split, orig_idx, text, coarse, fine, is_oos, annot, stem_key, hash_side, side,
        drop_reason)          item_id = "<corpus>:<orig_split>:<orig_idx>"
  provenance(corpus, name, url, sha256, bytes, fetched_utc)   one row per raw file
  meta(key PK, value)         normaliser, key rule, script blob (LF), split constants, attribution strings
Manifest: per-corpus raw / kept / dropped (by reason) / side counts / per-label side counts / labels below the minima
(< 10 EVAL or < 20 TRAIN) / components; items_sha256 = sha256 over
`SELECT item_id, corpus, text, coarse, fine, is_oos, side, drop_reason FROM items ORDER BY item_id`, repr + LF per row.

Launch sequence (run-operator, from main after the READY review; zero calls):
  python tools/ingest/intent_ingest.py --selftest                 # synthetic raw files in a temp dir; posts nothing
  python tools/ingest/intent_ingest.py --fetch                    # downloads the ABSENT raw files to RAW_DIR, then ingests
  python tools/ingest/intent_ingest.py --dry-run                  # parses RAW_DIR, prints counts + manifest, writes nothing
  python tools/ingest/intent_ingest.py                            # ingest from RAW_DIR (write-once DB)
  python tools/ingest/intent_ingest.py --manifest                 # re-read the DB, verify, write <db>.manifest.json (mode x)
Licences: MASSIVE CC BY 4.0; CLINC150 CC BY 3.0; BANKING77 CC BY 4.0. Attribution strings (ATTRIBUTION) are stored in meta
and printed in every outcome file. No corpus text is committed anywhere.
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import sqlite3
import sys
import tarfile
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "analysis"))
import split_side as SS  # noqa: E402

TAG = "[INTENT-INGEST]"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
DB_NAME = "intent_transfer_corpora_v1.db"
DEFAULT_OUT = os.path.join(DATA_ROOT, DB_NAME)
DEFAULT_RAW = os.path.join(os.environ.get("HF_HOME") or os.path.join(os.path.expanduser("~"), ".cache", "huggingface"),
                           "taxoarena_intent_raw")
PINS_FILE = os.path.join(ROOT, "experiment_configs", "intent_transfer_s0_pins.json")
PINS_SCHEMA = "intent_transfer_s0_pins/v1"
NEVER_WRITE = {"mmlu_pro_dataset_cache_v2.db", "embeddings_cache.db", "snapshots.db", "snapshots_frozen.db",
               "multicorpus_cache_v1.db", "embeddings_cache_nomic-embed-text_latest.db",
               "embeddings_cache_embeddinggemma_latest.db", "ratings.db"}
CORPORA = ("massive", "clinc", "banking77")
GOLD_K = {"massive": (18, 60), "clinc": (10, 150), "banking77": (None, 77)}     # registered K_c / K_f (fine excludes oos)
OOS = "oos"
MIN_EVAL, MIN_TRAIN = 10, 20                                                    # design section 5 per-label minima

SOURCES = {
    "massive": (("amazon-massive-dataset-1.1.tar.gz",
                 "https://amazon-massive-nlu-dataset.s3.amazonaws.com/amazon-massive-dataset-1.1.tar.gz"),),
    "clinc": (("clinc_data_oos_plus.json", "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_oos_plus.json"),
              ("clinc_domains.json", "https://raw.githubusercontent.com/clinc/oos-eval/master/data/domains.json")),
    "banking77": (("banking77_train.csv",
                   "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv"),
                  ("banking77_test.csv",
                   "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv")),
}
ATTRIBUTION = {
    "massive": "MASSIVE 1.1 en-US (FitzGerald et al., 2022), Amazon Science, CC BY 4.0, https://github.com/alexa/massive",
    "clinc": "CLINC150 / oos-eval, data_oos_plus (Larson et al., 2019), Clinc Inc., CC BY 3.0, https://github.com/clinc/oos-eval",
    "banking77": "BANKING77 (Casanueva et al., 2020), PolyAI, CC BY 4.0, https://github.com/PolyAI-LDN/task-specific-datasets",
}


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def script_blob(path=None):
    with open(path or os.path.abspath(__file__), "rb") as f:
        data = f.read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def _norm(p):
    return os.path.normcase(os.path.realpath(os.path.abspath(p)))


def _inside(p, root):
    p, root = _norm(p), _norm(root)
    return p == root or p.startswith(root.rstrip(os.sep) + os.sep)


def check_raw_dir(raw_dir):
    for r in {ROOT, DATA_ROOT}:
        if _inside(raw_dir, r):
            refuse("RAW_DIR %s is inside the repository / data root %s: raw corpus text never enters the repo "
                   "(data/**/*.jsonl is not ignored); name a directory outside it" % (raw_dir, r))


def load_pins(pins_file=None):
    pf = pins_file or PINS_FILE
    if not os.path.isfile(pf):
        return {"schema": PINS_SCHEMA, "raw": {}, "ingest_db": None, "emb": {}}
    with open(pf, encoding="utf-8") as f:
        pins = json.load(f)
    if pins.get("schema") != PINS_SCHEMA:
        refuse("%s: schema %r != %r" % (pf, pins.get("schema"), PINS_SCHEMA))
    return pins


# ------------------------------------------------------------------------------------------------ fetch (network; --fetch only)
def _download(url, timeout=120):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read()


_fetch = _download          # module-level so the selftest substitutes a stub (no network)


def fetch(raw_dir):
    """Download each ABSENT raw file (write to .part, rename). Never overwrites a present file."""
    os.makedirs(raw_dir, exist_ok=True)
    for corpus in CORPORA:
        for name, url in SOURCES[corpus]:
            p = os.path.join(raw_dir, name)
            if os.path.exists(p):
                print("%s %s present (%d bytes): not re-fetched" % (TAG, name, os.path.getsize(p)))
                continue
            data = _fetch(url)
            with open(p + ".part", "xb") as f:
                f.write(data)
            os.replace(p + ".part", p)
            print("%s fetched %s <- %s: %d bytes sha256 %s" % (TAG, name, url, len(data), sha_bytes(data)))


def read_raw(raw_dir, pins):
    """-> {name: bytes}, provenance rows. REFUSES an absent file (only --fetch downloads) and a pinned file whose sha differs."""
    out, prov = {}, []
    raw_pins = pins.get("raw") or {}
    for corpus in CORPORA:
        for name, url in SOURCES[corpus]:
            p = os.path.join(raw_dir, name)
            if not os.path.isfile(p):
                refuse("raw file %s absent in %s (only --fetch downloads)" % (name, raw_dir))
            with open(p, "rb") as f:
                b = f.read()
            s = sha_bytes(b)
            want = raw_pins.get(name)
            state = "UNPINNED (the registrar pins it after the first fetch)" if not want else ("PIN OK" if want == s else "PIN MISMATCH")
            print("%s raw %s: %d bytes sha256 %s [%s]" % (TAG, name, len(b), s, state))
            if want and want != s:
                refuse("raw %s sha256 %s != the pinned %s" % (name, s, want))
            out[name] = b
            prov.append((corpus, name, url, s, len(b),
                         datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%SZ")))
    return out, prov


# ------------------------------------------------------------------------------------------------ parsers (fail closed)
def _need(d, keys, where):
    miss = [k for k in keys if k not in d]
    if miss:
        refuse("%s: fields %s missing (fields seen: %s)" % (where, miss, sorted(d)[:20]))


def parse_massive(tar_bytes):
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:*") as tf:
        members = [m for m in tf.getmembers() if m.isfile() and m.name.replace("\\", "/").endswith("/data/en-US.jsonl")]
        if len(members) != 1:
            refuse("MASSIVE tarball: %d members end with /data/en-US.jsonl (need exactly 1)" % len(members))
        raw = tf.extractfile(members[0]).read().decode("utf-8")
    rows = []
    for ln, line in enumerate(raw.splitlines()):
        if not line.strip():
            continue
        d = json.loads(line)
        _need(d, ("id", "locale", "partition", "scenario", "intent", "utt", "annot_utt"), "MASSIVE en-US.jsonl line %d" % (ln + 1))
        if d["locale"] != "en-US":
            refuse("MASSIVE line %d: locale %r != en-US" % (ln + 1, d["locale"]))
        rows.append(dict(corpus="massive", orig_split=str(d["partition"]), orig_idx=str(d["id"]), text=d["utt"],
                         coarse=d["scenario"], fine=d["intent"], is_oos=0, annot=d["annot_utt"]))
    return rows


def parse_clinc(data_bytes, domains_bytes):
    data = json.loads(data_bytes.decode("utf-8"))
    domains = json.loads(domains_bytes.decode("utf-8"))
    _need(data, ("train", "val", "test", "oos_train", "oos_val", "oos_test"), "CLINC data_oos_plus.json")
    if not isinstance(domains, dict) or not all(isinstance(v, list) for v in domains.values()):
        refuse("CLINC domains.json is not a mapping domain -> [intent] (type %s)" % type(domains).__name__)
    fine2coarse = {}
    for dom, intents in domains.items():
        for it in intents:
            if it in fine2coarse:
                refuse("CLINC domains.json: intent %r in two domains (%s, %s)" % (it, fine2coarse[it], dom))
            fine2coarse[it] = dom
    rows = []
    for key in ("train", "val", "test", "oos_train", "oos_val", "oos_test"):
        for i, pair in enumerate(data[key]):
            if not (isinstance(pair, list) and len(pair) == 2):
                refuse("CLINC %s[%d] is not [text, intent]" % (key, i))
            text, lab = pair
            oos = key.startswith("oos_")
            if oos != (lab == OOS):
                refuse("CLINC %s[%d]: label %r in the %s list" % (key, i, lab, "oos" if oos else "in-scope"))
            if not oos and lab not in fine2coarse:
                refuse("CLINC %s[%d]: intent %r has no domain in domains.json" % (key, i, lab))
            rows.append(dict(corpus="clinc", orig_split=key, orig_idx=str(i), text=text,
                             coarse=OOS if oos else fine2coarse[lab], fine=lab, is_oos=int(oos), annot=None))
    return rows


def parse_banking(train_bytes, test_bytes):
    rows = []
    for split, b in (("train", train_bytes), ("test", test_bytes)):
        rd = csv.reader(io.StringIO(b.decode("utf-8")))
        header = next(rd, None)
        if header != ["text", "category"]:
            refuse("BANKING77 %s.csv header %r != ['text', 'category']" % (split, header))
        for i, r in enumerate(rd):
            if len(r) != 2:
                refuse("BANKING77 %s.csv row %d has %d fields" % (split, i + 1, len(r)))
            rows.append(dict(corpus="banking77", orig_split=split, orig_idx=str(i), text=r[0], coarse=None, fine=r[1],
                             is_oos=0, annot=None))
    return rows


def parse_all(raw):
    return (parse_massive(raw["amazon-massive-dataset-1.1.tar.gz"])
            + parse_clinc(raw["clinc_data_oos_plus.json"], raw["clinc_domains.json"])
            + parse_banking(raw["banking77_train.csv"], raw["banking77_test.csv"]))


# ------------------------------------------------------------------------------------------------ split + components
def assign(rows, gold_k=None):
    """Adds item_id, stem_key, hash_side, side, drop_reason. REFUSES a NUL byte, a duplicate item_id and a label count
    that is not the registered K (gold_k)."""
    gold_k = GOLD_K if gold_k is None else gold_k
    seen = set()
    for r in rows:
        if "\x00" in r["text"]:
            refuse("%s item %s:%s carries a NUL byte (never repaired)" % (r["corpus"], r["orig_split"], r["orig_idx"]))
        r["item_id"] = "%s:%s:%s" % (r["corpus"], r["orig_split"], r["orig_idx"])
        if r["item_id"] in seen:
            refuse("duplicate item_id %s" % r["item_id"])
        seen.add(r["item_id"])
        r["stem_key"] = SS.stem_key(r["text"])
        r["hash_side"] = SS.side_of_hash(SS.side_hash(r["stem_key"]))
        r["side"] = SS.EVAL if r["is_oos"] else r["hash_side"]
        r["drop_reason"] = "empty" if SS.norm(r["text"]) == "" else None
    for corpus in CORPORA:
        cr = [r for r in rows if r["corpus"] == corpus]
        kc, kf = gold_k[corpus]
        fines = set(r["fine"] for r in cr if not r["is_oos"])
        coarses = set(r["coarse"] for r in cr if not r["is_oos"])
        if len(fines) != kf or (kc is not None and len(coarses) != kc) or (kc is None and coarses != {None}):
            refuse("%s: %d fine / %d coarse labels != the registered K_f %s / K_c %s" % (corpus, len(fines), len(coarses), kf, kc))
        comps = {}
        for r in cr:
            comps.setdefault(r["stem_key"], []).append(r)
        for members in comps.values():
            labs = set(m["fine"] for m in members)
            if len(labs) > 1:
                why = "oos_collision" if OOS in labs else "cross_label"
                for m in members:
                    m["drop_reason"] = m["drop_reason"] or why
    return rows


def census(rows):
    """Printed counts (per corpus; side; drops; per-label minima; cross-corpus stem_key collisions)."""
    out = {}
    by_key = {}
    for r in rows:
        by_key.setdefault(r["stem_key"], set()).add(r["corpus"])
    out["cross_corpus_stem_keys"] = sum(1 for s in by_key.values() if len(s) > 1)
    for corpus in CORPORA:
        cr = [r for r in rows if r["corpus"] == corpus]
        kept = [r for r in cr if r["drop_reason"] is None]
        c = {"raw": len(cr), "kept": len(kept), "components": len(set(r["stem_key"] for r in kept)),
             "dropped": {}, "side": {}, "oos_side": {}, "hash_side_of_oos": {}, "labels_below_minima": []}
        for r in cr:
            if r["drop_reason"]:
                c["dropped"][r["drop_reason"]] = c["dropped"].get(r["drop_reason"], 0) + 1
        for r in kept:
            key = "oos_side" if r["is_oos"] else "side"
            c[key][r["side"]] = c[key].get(r["side"], 0) + 1
            if r["is_oos"]:
                c["hash_side_of_oos"][r["hash_side"]] = c["hash_side_of_oos"].get(r["hash_side"], 0) + 1
        per = {}
        for r in kept:
            if r["is_oos"]:
                continue
            per.setdefault(r["fine"], {SS.EVAL: 0, SS.GATE: 0, SS.TRAIN: 0})[r["side"]] += 1
        c["per_label"] = per
        c["labels_below_minima"] = sorted(l for l, s in per.items() if s[SS.EVAL] < MIN_EVAL or s[SS.TRAIN] < MIN_TRAIN)
        out[corpus] = c
    return out


def print_census(c):
    for corpus in CORPORA:
        x = c[corpus]
        print("%s %s: raw %d, kept %d (components %d), dropped %s; in-scope sides %s; OOS sides %s (their hash sides %s); "
              "labels below the minima (< %d EVAL or < %d TRAIN): %d %s"
              % (TAG, corpus, x["raw"], x["kept"], x["components"], json.dumps(x["dropped"], sort_keys=True),
                 json.dumps(x["side"], sort_keys=True), json.dumps(x["oos_side"], sort_keys=True),
                 json.dumps(x["hash_side_of_oos"], sort_keys=True), MIN_EVAL, MIN_TRAIN,
                 len(x["labels_below_minima"]), x["labels_below_minima"][:12]))
    print("%s cross-corpus stem_key collisions (disclosed; each corpus is read on its own): %d" % (TAG, c["cross_corpus_stem_keys"]))


# ------------------------------------------------------------------------------------------------ DB
DDL = (
    "CREATE TABLE items (item_id TEXT PRIMARY KEY, corpus TEXT NOT NULL, orig_split TEXT NOT NULL, orig_idx TEXT NOT NULL,"
    " text TEXT NOT NULL, coarse TEXT, fine TEXT NOT NULL, is_oos INTEGER NOT NULL, annot TEXT, stem_key TEXT NOT NULL,"
    " hash_side TEXT NOT NULL, side TEXT NOT NULL CHECK (side IN ('EVAL','GATE','TRAIN')), drop_reason TEXT)",
    "CREATE TABLE provenance (corpus TEXT, name TEXT PRIMARY KEY, url TEXT, sha256 TEXT, bytes INTEGER, fetched_utc TEXT)",
    "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)",
)
ITEM_COLS = ("item_id", "corpus", "orig_split", "orig_idx", "text", "coarse", "fine", "is_oos", "annot", "stem_key",
             "hash_side", "side", "drop_reason")


def check_out(out):
    if os.path.basename(out) in NEVER_WRITE:
        refuse("%s is a DB of record: never written" % out)
    for p in (out, out + "-wal", out + "-journal"):
        if os.path.lexists(p):
            refuse("%s exists: the study DB is write-once (remove it only on the registrar's word)" % p)


def write_db(out, rows, prov):
    check_out(out)
    open(out, "xb").close()                              # exclusive create (a racing file is never overwritten)
    con = sqlite3.connect(out)
    try:
        con.execute("PRAGMA journal_mode=DELETE")
        for d in DDL:
            con.execute(d)
        con.executemany("INSERT INTO items VALUES (%s)" % ",".join("?" * len(ITEM_COLS)),
                        [tuple(r[c] for c in ITEM_COLS) for r in sorted(rows, key=lambda r: r["item_id"])])
        con.executemany("INSERT INTO provenance VALUES (?,?,?,?,?,?)", prov)
        meta = {"normaliser_version": SS.NORMALISER_VERSION, "key_rule": SS.KEY_RULE,
                "split": json.dumps(SS.function_stamp()), "oos_rule": "every OOS row side=EVAL; hash_side kept",
                "script_blob_lf": script_blob(), "attribution": json.dumps(ATTRIBUTION, sort_keys=True),
                "gold_k": json.dumps(GOLD_K, sort_keys=True)}
        con.executemany("INSERT INTO meta VALUES (?,?)", sorted(meta.items()))
        con.commit()
    finally:
        con.close()
    for sfx in ("-wal", "-journal"):
        if os.path.exists(out + sfx) and os.path.getsize(out + sfx) > 0:
            refuse("%s%s is non-empty after the close" % (out, sfx))
    print("%s wrote %s: %d items, %d provenance rows; sha256 %s" % (TAG, out, len(rows), len(prov), file_sha(out)))


def file_sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def items_sha(con):
    h = hashlib.sha256()
    for row in con.execute("SELECT item_id, corpus, text, coarse, fine, is_oos, side, drop_reason FROM items ORDER BY item_id"):
        h.update((repr(row) + "\n").encode("utf-8"))
    return h.hexdigest()


def open_db_ro(path):
    for sfx in ("-wal", "-journal"):
        if os.path.exists(path + sfx) and os.path.getsize(path + sfx) > 0:
            refuse("%s%s is non-empty: refused (checkpoint first)" % (path, sfx))
    if not os.path.isfile(path):
        refuse("%s absent" % path)
    p = os.path.abspath(path).replace("\\", "/")
    return sqlite3.connect("file:%s%s?mode=ro&immutable=1" % ("" if p.startswith("/") else "/", p), uri=True)


def rows_from_db(con):
    return [dict(zip(ITEM_COLS, r)) for r in con.execute("SELECT %s FROM items ORDER BY item_id" % ",".join(ITEM_COLS))]


def manifest(path, write=True):
    if write and os.path.lexists(path + ".manifest.json"):
        refuse("%s.manifest.json exists: the manifest is write-once" % path)
    con = open_db_ro(path)
    try:
        rows = rows_from_db(con)
        # re-derive every side and drop from the text (the stored columns are asserted, never trusted)
        re_rows = assign([dict((k, r[k]) for k in ("corpus", "orig_split", "orig_idx", "text", "coarse", "fine", "is_oos", "annot"))
                          for r in rows])
        bad = [a["item_id"] for a, b in zip(sorted(re_rows, key=lambda r: r["item_id"]), rows)
               if (a["item_id"], a["stem_key"], a["side"], a["drop_reason"]) != (b["item_id"], b["stem_key"], b["side"], b["drop_reason"])]
        if bad:
            refuse("%d stored rows disagree with the recomputed side / key / drop (first %s)" % (len(bad), bad[:3]))
        prov = con.execute("SELECT corpus, name, url, sha256, bytes FROM provenance ORDER BY name").fetchall()
        m = {"db": os.path.basename(path), "sha256": file_sha(path), "items_sha256": items_sha(con), "census": census(rows),
             "provenance": prov, "script_blob_lf": script_blob()}
    finally:
        con.close()
    print_census(m["census"])
    print("%s manifest: items_sha256 %s; db sha256 %s; rows recomputed and equal (%d)" % (TAG, m["items_sha256"], m["sha256"], len(rows)))
    if write:
        with open(path + ".manifest.json", "x", encoding="utf-8") as f:
            json.dump(m, f, indent=1, sort_keys=True)
        print("%s wrote %s.manifest.json" % (TAG, path))
    return m


# ------------------------------------------------------------------------------------------------ selftest
def _fixture_raw(d, nul=False, bad_k=False, oos_collide=True):
    """Synthetic raw files with the registered K (18/60, 10/150, 77); texts are synthetic tokens, never corpus text."""
    lines = []
    for i in range(60 if not bad_k else 59):
        for j in range(4):
            lines.append(json.dumps({"id": "%d" % (i * 4 + j), "locale": "en-US", "partition": ["train", "dev", "test", "train"][j],
                                     "scenario": "sc%02d" % (i % 18), "intent": "sc%02d_in%02d" % (i % 18, i),
                                     "utt": "massive utt %d %d%s" % (i, j, "\x00" if nul and i == 3 and j == 1 else ""),
                                     "annot_utt": "massive utt [date : %d] %d" % (i, j)}))
    lines.append(json.dumps({"id": "dup1", "locale": "en-US", "partition": "train", "scenario": "sc00", "intent": "sc00_in00",
                             "utt": "MASSIVE  utt 0 0", "annot_utt": "x"}))           # a norm-v1 duplicate, same label: kept
    lines.append(json.dumps({"id": "xl1", "locale": "en-US", "partition": "train", "scenario": "sc01", "intent": "sc01_in01",
                             "utt": "massive utt 0 1", "annot_utt": "x"}))            # a cross-label duplicate: both dropped
    tb = io.BytesIO()
    with tarfile.open(fileobj=tb, mode="w:gz") as tf:
        data = ("\n".join(lines) + "\n").encode("utf-8")
        ti = tarfile.TarInfo("1.1/data/en-US.jsonl")
        ti.size = len(data)
        tf.addfile(ti, io.BytesIO(data))
    files = {"amazon-massive-dataset-1.1.tar.gz": tb.getvalue()}
    domains = {"dom%d" % k: ["in%03d" % i for i in range(150) if i % 10 == k] for k in range(10)}
    data = {k: [] for k in ("train", "val", "test", "oos_train", "oos_val", "oos_test")}
    for i in range(150):
        for j in range(3):
            data[["train", "val", "test"][j]].append(["clinc text %d %d" % (i, j), "in%03d" % i])
    for j in range(30):
        data[["oos_train", "oos_val", "oos_test"][j % 3]].append(["oos text %d" % j, "oos"])
    if oos_collide:
        data["oos_test"].append(["Clinc text 5 0", "oos"])                              # collides with in-scope: dropped
    files["clinc_data_oos_plus.json"] = json.dumps(data).encode("utf-8")
    files["clinc_domains.json"] = json.dumps(domains).encode("utf-8")
    for split, n in (("train", 3), ("test", 1)):
        s = io.StringIO()
        w = csv.writer(s, lineterminator="\n")
        w.writerow(["text", "category"])
        for i in range(77):
            for j in range(n):
                w.writerow(["bank %s %d %d" % (split, i, j), "cat%02d" % i])
        files["banking77_%s.csv" % split] = s.getvalue().encode("utf-8")
    for name, b in files.items():
        with open(os.path.join(d, name), "wb") as f:
            f.write(b)
    return files


def _quiet(fn, *a, **k):
    import contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


def _expect_refusal(fn, needle):
    try:
        fn()
    except SystemExit as e:
        assert needle in str(e), "refusal %r lacks %r" % (str(e)[:200], needle)
        return str(e)
    raise AssertionError("no refusal (expected %r)" % needle)


def selftest(quiet=False):
    global _fetch
    n = [0]

    def ok(c, what):
        if not c:
            raise AssertionError("SELFTEST FAILED: " + what)
        n[0] += 1
        if not quiet:
            print("  ok  " + what)
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw")
        os.makedirs(raw)
        files = _fixture_raw(raw)
        out = os.path.join(td, "db", DB_NAME)
        os.makedirs(os.path.dirname(out))
        empty_pins = os.path.join(td, "pins.json")
        with open(empty_pins, "w") as f:
            json.dump({"schema": PINS_SCHEMA, "raw": {}, "ingest_db": None, "emb": {}}, f)
        rc = main(["--raw-dir", raw, "--out", out, "--pins", empty_pins], quiet=True)
        ok(rc == 0 and os.path.isfile(out), "II-INGEST ingest of the synthetic raw files writes the DB")
        con = open_db_ro(out)
        rows = rows_from_db(con)
        con.close()
        by = {r["item_id"]: r for r in rows}
        ok(len(rows) == 60 * 4 + 2 + 450 + 31 + 77 * 4, "II-COUNT every raw row stored (%d)" % len(rows))
        for r in rows:
            assert r["stem_key"] == SS.stem_key(r["text"])
            assert r["hash_side"] == SS.side_of_hash(SS.side_hash(r["stem_key"]))
            assert r["side"] == (SS.EVAL if r["is_oos"] else r["hash_side"])
        ok(True, "II-SIDE every side = side_of_hash(side_hash(stem_key)); every OOS row EVAL")
        oos_hash_nonEval = sum(1 for r in rows if r["is_oos"] and r["hash_side"] != SS.EVAL)
        ok(oos_hash_nonEval > 0, "II-OOS the fixture has OOS rows whose HASH side is not EVAL (%d), stored side EVAL" % oos_hash_nonEval)
        ok(by["massive:train:dup1"]["drop_reason"] is None and by["massive:train:dup1"]["side"] == by["massive:train:0"]["side"],
           "II-DUP a norm-v1 duplicate with the same label is kept and shares the side")
        ok(by["massive:train:xl1"]["drop_reason"] == "cross_label" and by["massive:dev:1"]["drop_reason"] == "cross_label",
           "II-XLABEL both members of a cross-label component are dropped")
        coll = [r for r in rows if r["corpus"] == "clinc" and r["stem_key"] == SS.stem_key("clinc text 5 0")]
        ok(len(coll) == 2 and all(r["drop_reason"] == "oos_collision" for r in coll),
           "II-OOSCOLL an OOS row colliding with an in-scope row: the whole component dropped (oos_collision)")
        ok(all(r["coarse"] is None for r in rows if r["corpus"] == "banking77"), "II-BANK banking77 carries no coarse level")
        clinc_in = [r for r in rows if r["corpus"] == "clinc" and not r["is_oos"]]
        ok(all(r["coarse"] == "dom%d" % (int(r["fine"][2:]) % 10) for r in clinc_in), "II-DOMAIN CLINC coarse = domains.json's domain")
        _expect_refusal(lambda: main(["--raw-dir", raw, "--out", out, "--pins", empty_pins], quiet=True), "write-once")
        ok(True, "II-ONCE a second ingest to the same path REFUSES (write-once)")
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            m = manifest(out, write=True)
        ok(os.path.isfile(out + ".manifest.json") and m["census"]["clinc"]["dropped"] == {"oos_collision": 2},
           "II-MANIFEST manifest recomputes every row, counts the drops and writes the json (mode x)")
        _expect_refusal(lambda: manifest(out, write=True), "write-once")
        ok(True, "II-MANIFEST-ONCE the manifest json is write-once")
        # tampered DB: a stored side that disagrees with the recomputation REFUSES
        tam = os.path.join(td, "tam.db")
        with open(out, "rb") as s, open(tam, "wb") as d:
            d.write(s.read())
        c2 = sqlite3.connect(tam)
        vic = c2.execute("SELECT item_id, side FROM items WHERE is_oos=0 AND side='TRAIN' LIMIT 1").fetchone()
        c2.execute("UPDATE items SET side='EVAL' WHERE item_id=?", (vic[0],))
        c2.commit()
        c2.close()
        _expect_refusal(lambda: _quiet(manifest, tam, write=False), "disagree with the recomputed")
        ok(True, "II-TAMPER a stored side flipped TRAIN -> EVAL is REFUSED by the manifest's recomputation")
        # refusals
        for name, kw, needle in (("NUL", dict(nul=True), "NUL byte"), ("K", dict(bad_k=True), "registered K_f")):
            r2 = os.path.join(td, "raw_" + name)
            os.makedirs(r2)
            _fixture_raw(r2, **kw)
            _expect_refusal(lambda: main(["--raw-dir", r2, "--out", os.path.join(td, name + ".db"), "--pins", empty_pins], quiet=True), needle)
            ok(not os.path.exists(os.path.join(td, name + ".db")), "II-REFUSE-%s refused before any write (%s)" % (name, needle))
        pinned = os.path.join(td, "pins2.json")
        with open(pinned, "w") as f:
            json.dump({"schema": PINS_SCHEMA, "raw": {"clinc_domains.json": "0" * 64}, "ingest_db": None, "emb": {}}, f)
        _expect_refusal(lambda: main(["--raw-dir", raw, "--out", os.path.join(td, "p.db"), "--pins", pinned], quiet=True), "pinned")
        ok(True, "II-PIN a raw file whose sha256 differs from its pin REFUSES")
        with open(pinned, "w") as f:
            json.dump({"schema": PINS_SCHEMA, "raw": {k: sha_bytes(v) for k, v in files.items()}, "ingest_db": None, "emb": {}}, f)
        ok(main(["--raw-dir", raw, "--out", os.path.join(td, "p.db"), "--pins", pinned], quiet=True) == 0, "II-PIN-OK matching pins ingest")
        _expect_refusal(lambda: main(["--raw-dir", os.path.join(ROOT, "tmp_raw"), "--dry-run", "--pins", empty_pins], quiet=True),
                        "inside the repository")
        ok(True, "II-RAWDIR a RAW_DIR inside the repo REFUSES")
        _expect_refusal(lambda: check_out(os.path.join(td, "embeddings_cache.db")), "DB of record")
        ok(True, "II-RECORD the DB of record is refused by name")
        # --fetch downloads only absent files, through the stub (no network)
        fr = os.path.join(td, "fetch")
        os.makedirs(fr)
        calls = []
        saved = _fetch
        _fetch = lambda url: (calls.append(url), files[[nm for c in CORPORA for nm, u in SOURCES[c] if u == url][0]])[1]
        try:
            with open(os.path.join(fr, "banking77_test.csv"), "wb") as f:
                f.write(files["banking77_test.csv"])
            rc = main(["--fetch", "--raw-dir", fr, "--out", os.path.join(td, "f.db"), "--pins", empty_pins], quiet=True)
        finally:
            _fetch = saved
        ok(rc == 0 and len(calls) == 4, "II-FETCH --fetch downloads the 4 absent files only (%d), then ingests" % len(calls))
        # dry-run writes nothing
        before = sorted(os.listdir(td))
        ok(main(["--raw-dir", raw, "--dry-run", "--out", os.path.join(td, "dry.db"), "--pins", empty_pins], quiet=True) == 0
           and sorted(os.listdir(td)) == before, "II-DRY --dry-run writes nothing")
    print("%s SELFTEST PASSED (%d checks)" % (TAG, n[0]))
    return 0


MUTANTS = (
    ("OOS side not forced EVAL", "        r[\"side\"] = SS.EVAL if r[\"is_oos\"] else r[\"hash_side\"]\n",
     "        r[\"side\"] = r[\"hash_side\"]\n"),
    ("side from the raw text, not the stem key", "        r[\"hash_side\"] = SS.side_of_hash(SS.side_hash(r[\"stem_key\"]))\n",
     "        r[\"hash_side\"] = SS.side_of_hash(SS.side_hash(r[\"text\"]))\n"),
    ("cross-label component kept", "            if len(labs) > 1:\n", "            if False:\n"),
    ("only the OOS member of a collision dropped", "                for m in members:\n                    m[\"drop_reason\"] = m[\"drop_reason\"] or why\n",
     "                for m in members:\n                    if m[\"is_oos\"] or why != \"oos_collision\":\n                        m[\"drop_reason\"] = m[\"drop_reason\"] or why\n"),
    ("collision labelled cross_label", "                why = \"oos_collision\" if OOS in labs else \"cross_label\"\n", "                why = \"cross_label\"\n"),
    ("NUL admitted", "        if \"\\x00\" in r[\"text\"]:\n", "        if False:\n"),
    ("registered K unchecked", "        if len(fines) != kf or", "        if False and len(fines) != kf or"),
    ("DB not write-once", "    for p in (out, out + \"-wal\", out + \"-journal\"):\n        if os.path.lexists(p):\n", "    for p in ():\n        if os.path.lexists(p):\n"),
    ("DB of record admitted", "    if os.path.basename(out) in NEVER_WRITE:\n", "    if False:\n"),
    ("RAW_DIR inside the repo admitted", "        if _inside(raw_dir, r):\n", "        if False:\n"),
    ("raw pin mismatch admitted", "            if want and want != s:\n", "            if False:\n"),
    ("manifest trusts the stored columns", "        if bad:\n            refuse(\"%d stored rows disagree", "        if False:\n            refuse(\"%d stored rows disagree"),
    ("manifest not write-once", "    if write and os.path.lexists(path + \".manifest.json\"):\n", "    if False:\n"),
    ("--fetch re-downloads present files", "            if os.path.exists(p):\n                print(\"%s %s present", "            if False:\n                print(\"%s %s present"),
    ("dry-run writes", "        if a.dry_run:\n            print(\"%s dry: nothing written", "        if False:\n            print(\"%s dry: nothing written"),
    ("banking77 coarse invented", "rows.append(dict(corpus=\"banking77\", orig_split=split, orig_idx=str(i), text=r[0], coarse=None,",
     "rows.append(dict(corpus=\"banking77\", orig_split=split, orig_idx=str(i), text=r[0], coarse=\"banking\","),
    ("CLINC domain map ignored", "                             coarse=OOS if oos else fine2coarse[lab], fine=lab,", "                             coarse=OOS if oos else \"dom0\", fine=lab,"),
)


def run_mutants():
    """Each mutant is a one-line source edit of this file, executed in a fresh namespace; the whole selftest must fail."""
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head, tail = src[:cut] + src[end:], ""          # every function (main included) is mutable; the table itself is not
    killed = 0
    for name, old, new in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "intent_ingest_mutant", "__file__": os.path.abspath(__file__)}
        import contextlib
        try:
            exec(compile(head.replace(old, new) + tail, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](quiet=True)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            res = "KILLED | %s" % (str(ex).splitlines()[0][:100] if str(ex) else type(ex).__name__)
        killed += res.startswith("KILLED")
        print("  %-44s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None, quiet=False):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mutants", action="store_true")
    ap.add_argument("--fetch", action="store_true", help="download the absent raw files (network), then ingest")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--raw-dir", default=DEFAULT_RAW)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--pins", default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.manifest:
        manifest(a.out, write=True)
        return 0
    check_raw_dir(a.raw_dir)
    pins = load_pins(a.pins)
    if not a.dry_run:
        check_out(a.out)
    if a.fetch:
        fetch(a.raw_dir)
    import contextlib
    ctx = contextlib.redirect_stdout(io.StringIO()) if quiet else contextlib.nullcontext()
    with ctx:
        raw, prov = read_raw(a.raw_dir, pins)
        rows = assign(parse_all(raw))
        print_census(census(rows))
        if a.dry_run:
            print("%s dry: nothing written (%d items would be stored in %s)" % (TAG, len(rows), a.out))
            return 0
        write_db(a.out, rows, prov)
    return 0


if __name__ == "__main__":
    sys.exit(main())
