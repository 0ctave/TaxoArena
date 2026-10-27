"""data_v2.ingest (M1): one sealed corpus_v2 DB per corpus version, four id levels, read-only on the sources (ARCH-v2 E-D).

Levels (data §1; SYNTHESIS Stage D):
  item(item_id = "i:"+stem_key)                  one row per split_side.stem_key (norm-v1, options-free); origin
                                                 'corpus' (some upstream corpus row has this stem) or 'response' (only a
                                                 model response row carries it, e.g. Llama's id-shifted texts)
  variant(variant_id = "v:"+content_key)         stem + SORTED options (opt-v1 extractor) + contract (the verifier):
                                                 shuffled copies collapse; stem-only variants stay distinct variants of
                                                 one item; answer_text_norm is NULL when the rows of one variant disagree
                                                 (n_answer_texts > 1: flagged, never resolved)
  source_row                                     EVERY upstream corpus row, sentinels included, with its own order
                                                 (options_ordered_sha) and its own letter; the legacy ids are ALIASES
  label / label_conflict                         a conflict within (item, scheme) is FLAGGED, never resolved
  answer_class                                   content_closure.label_conflicts per item (the four answer classes)
  item_subset                                    content_closure.one_row_per_key over GPQA rows (subset tags)
  response(seen_ck)                              every upstream response row; seen_ck is the variant the model was
                                                 shown, keyed from ITS OWN text and options (no join to a corpus row)
  options_ordered                                the VERBATIM ordered options_json of every source row and response,
                                                 content-addressed by options_ordered_sha (sha256 over "N" for NULL or
                                                 "S"+raw, first 32 hex; zlib), so the letters a model answered with can be
                                                 rendered where the option order differs between models (173-205 qids)
  reference / reference_unresolved               LEGACY reference vintages keyed by variant_id with vintage and
                                                 side_at_mint (R9); the crossing is by the response table's id alias and
                                                 the content key of the row the solver saw, never question_text (see
                                                 LEGACY_REFERENCES); anything ambiguous is unresolved, never guessed
  retired_legacy_flag                            the retired upstream is_reserved flag, kept ONLY as a legacy alias for
                                                 audits of the old id split (the G2 positive-control family); it is not in
                                                 `response`, not in any view, and the v2 split / view code never names it
  model_registry                                 Meta-Llama-3-70B-Instruct QUARANTINED
  quarantine_check                               per quarantined model: rows whose own stem differs from the modal stem of
                                                 the active models' rows of the same legacy qid (definition printed; the
                                                 record's 7,424 of 7,510 is printed beside it, never tuned)

No join anywhere uses question text or an options key: every row is keyed by its own content. The legacy links
(eval_question_link, the engine's p2dca id universe) are stored ONLY as alias rows (namespace 'legacy_*') so the old split can
be reproduced as a positive control (gates G2); no v2 table is derived from them.

Sources are opened read-only through data_v2.ro.open_ro (the -wal / -journal check, then mode=ro&immutable=1, query_only).
Only the declared tables are read; a foreign table in a source DB (ag_news in the MMLU-Pro DB, 2,000 rows) is NOT ingested
and is named in meta.excluded_tables.
"""
import json
import os
import zlib
from collections import Counter, defaultdict

from . import common as C
from . import ro

SUBSET_SOURCES = ("GPQA",)
# The closed list of answer contracts (the verifier strings of the corpora of record). variant.contract_id carries a
# CHECK on exactly this list and ingestion refuses any other value before the insert. The contract -> corpus-type map
# (how a contract is judged) is E-J's, not this layer's.
CONTRACTS = ("MC_LETTER", "IMPORTED:acc_norm", "IMPORTED:exact_match", "IMPORTED:prompt_level_strict_acc")
# Retired upstream columns (common.RETIRED_NAMES): stored ONLY in their own table, never in `response`, never in a view.

# LEGACY REFERENCES (R9: keyed by variant_id; E-D ingests the legacy vintages, E-J mints new ones). The legacy solver
# (tools/analysis/judge_solve_map.py questions(), L59-L76) was shown the eval row of SOLVER_MODEL for its question_id,
# and when that row is missing an unordered non-Llama row. The crossing to a variant is therefore:
#   (1) resolution 'solver_row': the seen_ck of the response (legacy_qid, SOLVER_MODEL) in THIS corpus (the id alias of
#       the response table + the content key of what the solver saw; never question_text);
#   (2) resolution 'unique_active_variant': no SOLVER_MODEL row, and every ACTIVE row of the qid carries ONE seen_ck;
#   (3) otherwise the row goes to reference_unresolved with its candidate variants (never guessed).
# side_at_mint: copied from the cache where it has the column (v1); for v0 it is DERIVED from the pool of record at mint
# time (the p2dca id file, id-only): "EVAL" when the qid is a listed judgeable id, "NOT_LISTED" otherwise.
# [DOCUMENTED 2026-09-24 on READY_archv2_ED D8, behaviour unchanged] side_at_mint is FREE TEXT ("EVAL" for v0, "EVAL (pool
# of record)" copied for v1), it is ID-ONLY, and it names the OLD split (p2dca21ab5f4ef3ae), NEVER the v2 split: on ED2,
# 2,539 references sitting on the v2 generation side carry "EVAL". NO CONSUMER MAY READ side_at_mint AS A v2 SIDE; the v2
# side of a reference is the split's side of its item (reference.item_id -> split `side`). A closed vocabulary and a
# side_at_mint_pool column are the reviewer's proposed follow-up, not built here.
SOLVER_MODEL = "gpt-4o-2024-08-06"
LEGACY_REFERENCES = {
    "mmlu-pro-v2": [
        {"vintage": "grok-reasoning-v0", "db": "experiment_results/judge_solve/grok-reasoning.db",
         "side_pool_file": "experiment_configs/reserved_pool_frozen_p2dca.json", "side_pool_id": "p2dca21ab5f4ef3ae"},
        {"vintage": "grok-reasoning-v1", "db": "experiment_results/judge_solve/grok-reasoning-v1.db",
         "side_pool_file": None, "side_pool_id": None},
    ],
}
REFERENCE_COLS = ("answer", "gt", "correct", "raw", "state", "finish_reason", "response_id", "reference_model",
                  "protocol_id", "max_tokens", "temperature", "completion_tokens", "latency", "minted_at")
# The record's Llama figure (CONTEXT rule 6; data §1 "the record says 7,424 of 7,510"), printed beside the computed one.
QUARANTINE_RECORD = {("mmlu-pro-v2", "Meta-Llama-3-70B-Instruct"): (7424, 7510)}


def _sha(obj):
    import hashlib
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


# ── the two corpus specs ────────────────────────────────────────────────────────────────────

def _mmlu_source_rows(conn):
    for mid, q, cat, opts, ans in conn.execute("SELECT id, question, category, options, answer FROM mmlu_pro ORDER BY id"):
        yield {"table": "mmlu_pro", "upstream_pk": mid, "upstream_id": str(mid), "source": "MMLU_PRO", "subset_tag": None,
               "text": q, "options_json": opts, "gt": ans, "contract": "MC_LETTER", "domain": cat,
               "labels": {"mmlu_pro.category": cat},
               "raw": [mid, q, cat, opts, ans]}


def _mmlu_responses(conn):
    for qid, model, cat, qt, oj, gt, pred, out, ok, res in conn.execute(
            "SELECT question_id, model_name, category, question_text, options_json, gt_answer, pred, model_output,"
            " is_correct, is_reserved FROM eval_results ORDER BY question_id, model_name"):
        yield {"legacy_qid": qid, "model": model, "category": cat, "text": qt, "options_json": oj, "gt": gt, "pred": pred,
               "output": out, "is_correct": ok, "is_correct_mathfix": None, "legacy_is_reserved": res,
               "contract": "MC_LETTER", "source": "MMLU_PRO"}


def _mmlu_aliases(conn):
    """legacy_eval_question_link: qid -> mmlu_pro row (the retired link, kept as an alias only);
    legacy_p2dca_engine_id: the engine's id universe (MMLUDatasetFetcher.loadFromDb: a linked row carries its eval
    question_id, an unlinked one -1,000,000 - rowid), one alias per join row in mmlu_pro.id order (last row wins on a
    repeated id, as content_closure._load_p2dca)."""
    for qid, mid in conn.execute("SELECT question_id, mmlu_pro_row_id FROM eval_question_link ORDER BY question_id"):
        if mid is not None:
            yield ("legacy_eval_question_link", str(qid), ("mmlu_pro", mid))
    seq = 0
    for mid, lq in conn.execute("SELECT m.id, l.question_id FROM mmlu_pro m LEFT JOIN eval_question_link l"
                                " ON m.id = l.mmlu_pro_row_id ORDER BY m.id ASC"):
        q = lq if (lq is not None and lq > 0) else -1000000 - mid
        seq += 1
        yield ("legacy_p2dca_engine_id", str(q), ("mmlu_pro", mid), seq)


def _union_source_rows(conn):
    for qid, src, up, task, dom, text, oj, tgt, ver, gen in conn.execute(
            "SELECT question_id, source, upstream_id, task, domain, text, options_json, target, verifier, generative"
            " FROM corpus_questions ORDER BY question_id"):
        yield {"table": "corpus_questions", "upstream_pk": qid, "upstream_id": "%s:%s" % (src, up), "source": src,
               "subset_tag": task, "text": text, "options_json": oj, "gt": tgt, "contract": ver, "domain": dom,
               "labels": {"union.source": src, "union.domain": dom, "union.task": task},
               "raw": [qid, src, up, task, dom, text, oj, tgt, ver, gen]}


def _union_responses(conn):
    contract = {q: (s, v) for q, s, v in conn.execute("SELECT question_id, source, verifier FROM corpus_questions")}
    fix = {(q, m): ok for q, m, ok in conn.execute("SELECT question_id, model_name, is_correct FROM eval_results_mathfix")}
    for qid, model, cat, qt, oj, gt, pred, out, ok, res in conn.execute(
            "SELECT question_id, model_name, category, question_text, options_json, gt_answer, pred, model_output,"
            " is_correct, is_reserved FROM eval_results ORDER BY question_id, model_name"):
        # The response's contract (verifier) and source are read from the upstream PK of the SAME corpus table (an id
        # lookup, not a content join); its variant is keyed from its own text and options.
        src, ver = contract[qid]
        yield {"legacy_qid": qid, "model": model, "category": cat, "text": qt, "options_json": oj, "gt": gt, "pred": pred,
               "output": out, "is_correct": ok, "is_correct_mathfix": fix.get((qid, model)), "legacy_is_reserved": res,
               "contract": ver, "source": src}


def _union_aliases(conn):
    for qid, src, up in conn.execute("SELECT question_id, source, upstream_id FROM corpus_questions ORDER BY question_id"):
        yield ("legacy_union_question_id", str(qid), ("corpus_questions", qid))


SPECS = {
    "mmlu-pro-v2": {
        "db": "mmlu_pro_dataset_cache_v2.db", "file_tag": "mmlu_pro_v2",
        "tables_read": ["mmlu_pro", "eval_results", "eval_question_link"],
        "excluded_tables": ["ag_news (2,000 rows: a foreign corpus in this DB; data §1, D9)", "reserved_pool",
                            "reserved_pool_meta", "active_reserved_pool", "corpus_registry"],
        "source_rows": _mmlu_source_rows, "responses": _mmlu_responses, "aliases": _mmlu_aliases,
        "domain_scheme": "mmlu_pro.category",
        "record": {"source_rows": 12000, "items_corpus": 11609, "responses": 560379},
    },
    "mc6-2026-09-11": {
        "db": "multicorpus_cache_v1.db", "file_tag": "union_mc6",
        "tables_read": ["corpus_questions", "eval_results", "eval_results_mathfix"],
        "excluded_tables": ["reserved_pool", "reserved_pool_meta", "active_reserved_pool", "corpus_registry",
                            "eval_question_link (0 rows)", "mmlu_pro (0 rows)"],
        "source_rows": _union_source_rows, "responses": _union_responses, "aliases": _union_aliases,
        "domain_scheme": "union.domain",
        "record": {"source_rows": 21606, "items_corpus": 20535, "gpqa_items": 546, "responses": 388908},
    },
}

DDL = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE item (item_id TEXT PRIMARY KEY, stem_key TEXT NOT NULL UNIQUE, family_id TEXT, origin TEXT NOT NULL
    CHECK (origin IN ('corpus','response')), n_variants INTEGER NOT NULL, n_source_rows INTEGER NOT NULL,
    n_responses INTEGER NOT NULL) WITHOUT ROWID;
CREATE TABLE variant (variant_id TEXT PRIMARY KEY, item_id TEXT NOT NULL REFERENCES item(item_id),
    contract_id TEXT NOT NULL CHECK (contract_id IN (%CONTRACTS%)),
    stem TEXT NOT NULL, options_sorted_json TEXT NOT NULL, answer_text_norm TEXT, n_answer_texts INTEGER NOT NULL,
    origin TEXT NOT NULL CHECK (origin IN ('corpus','response')), n_source_rows INTEGER NOT NULL,
    n_responses INTEGER NOT NULL) WITHOUT ROWID;
CREATE TABLE source_row (source_row_id TEXT PRIMARY KEY, corpus_table TEXT NOT NULL, upstream_pk INTEGER NOT NULL,
    upstream_id TEXT NOT NULL, source TEXT NOT NULL, domain TEXT, subset_tag TEXT, variant_id TEXT NOT NULL REFERENCES variant(variant_id),
    item_id TEXT NOT NULL REFERENCES item(item_id), text TEXT NOT NULL, options_json_raw TEXT, options_ordered_sha TEXT NOT NULL,
    gt_raw TEXT, answer_text TEXT, raw_sha256 TEXT NOT NULL, UNIQUE (corpus_table, upstream_pk)) WITHOUT ROWID;
CREATE TABLE alias (namespace TEXT NOT NULL, legacy_id TEXT NOT NULL, target_kind TEXT NOT NULL, target_id TEXT NOT NULL,
    seq INTEGER NOT NULL, n INTEGER NOT NULL, PRIMARY KEY (namespace, legacy_id, target_id, seq)) WITHOUT ROWID;
CREATE TABLE label (item_id TEXT NOT NULL, label_scheme TEXT NOT NULL, label TEXT NOT NULL, n_rows INTEGER NOT NULL,
    PRIMARY KEY (item_id, label_scheme, label)) WITHOUT ROWID;
CREATE TABLE label_conflict (item_id TEXT NOT NULL, label_scheme TEXT NOT NULL, labels_json TEXT NOT NULL,
    PRIMARY KEY (item_id, label_scheme)) WITHOUT ROWID;
CREATE TABLE answer_class (item_id TEXT PRIMARY KEY, class TEXT NOT NULL, targets_json TEXT NOT NULL,
    source_rows_json TEXT NOT NULL) WITHOUT ROWID;
CREATE TABLE item_subset (item_id TEXT NOT NULL, tag TEXT NOT NULL, representative_row TEXT NOT NULL,
    PRIMARY KEY (item_id, tag)) WITHOUT ROWID;
CREATE TABLE model_registry (model TEXT PRIMARY KEY, status TEXT NOT NULL CHECK (status IN ('ACTIVE','QUARANTINED')),
    reason TEXT, n_responses INTEGER NOT NULL) WITHOUT ROWID;
CREATE TABLE response (response_id TEXT PRIMARY KEY, model TEXT NOT NULL REFERENCES model_registry(model),
    legacy_qid INTEGER NOT NULL, source TEXT NOT NULL, seen_ck TEXT NOT NULL REFERENCES variant(variant_id),
    item_id TEXT NOT NULL REFERENCES item(item_id), options_ordered_sha TEXT NOT NULL, gt_raw TEXT, answer_text TEXT,
    pred TEXT, is_correct INTEGER NOT NULL, is_correct_mathfix INTEGER,
    category TEXT NOT NULL, output_sha256 TEXT NOT NULL, output_zlib BLOB NOT NULL,
    UNIQUE (model, legacy_qid)) WITHOUT ROWID;
CREATE TABLE options_ordered (options_ordered_sha TEXT PRIMARY KEY, is_null INTEGER NOT NULL CHECK (is_null IN (0, 1)),
    codec TEXT NOT NULL CHECK (codec = 'zlib'), options_json_zlib BLOB NOT NULL) WITHOUT ROWID;
CREATE TABLE retired_legacy_flag (response_id TEXT PRIMARY KEY REFERENCES response(response_id),
    legacy_is_reserved INTEGER NOT NULL) WITHOUT ROWID;
CREATE TABLE reference (variant_id TEXT NOT NULL REFERENCES variant(variant_id), vintage TEXT NOT NULL,
    source_key TEXT NOT NULL, item_id TEXT NOT NULL REFERENCES item(item_id), legacy_qid INTEGER,
    side_at_mint TEXT NOT NULL, side_at_mint_rule TEXT NOT NULL, resolution TEXT NOT NULL,
    answer TEXT, gt TEXT, correct INTEGER, raw TEXT, state TEXT, finish_reason TEXT, response_id TEXT, reference_model TEXT,
    protocol_id TEXT, max_tokens INTEGER, temperature TEXT, completion_tokens INTEGER, latency REAL, minted_at TEXT,
    source_db TEXT NOT NULL, source_db_sha256_bytes TEXT NOT NULL,
    PRIMARY KEY (variant_id, vintage, source_key)) WITHOUT ROWID;
CREATE TABLE reference_unresolved (vintage TEXT NOT NULL, source_key TEXT NOT NULL, legacy_qid INTEGER, reason TEXT NOT NULL,
    candidate_variants_json TEXT NOT NULL, answer TEXT, raw TEXT, source_db TEXT NOT NULL,
    PRIMARY KEY (vintage, source_key)) WITHOUT ROWID;
CREATE INDEX idx_reference_item ON reference(item_id);
CREATE TABLE quarantine_check (model TEXT PRIMARY KEY, n_rows INTEGER NOT NULL, n_content_mismatch INTEGER NOT NULL,
    n_no_active_row INTEGER NOT NULL, definition TEXT NOT NULL) WITHOUT ROWID;
CREATE INDEX idx_response_item ON response(item_id);
CREATE INDEX idx_response_seen ON response(seen_ck);
CREATE INDEX idx_source_row_item ON source_row(item_id);
CREATE INDEX idx_variant_item ON variant(item_id);
""".replace("%CONTRACTS%", ", ".join("'%s'" % c for c in CONTRACTS))


def build_corpus(corpus_version, out_dir, out=print, data_root=None, repo_root=None):
    """Build and SEAL corpus_v2_<tag>.db from the source DB of `corpus_version` (read-only). Returns the manifest entry.
    repo_root locates the id files of LEGACY_REFERENCES (default: this checkout; the selftest passes its fixture root)."""
    repo_root = repo_root or C.ROOT
    spec = SPECS.get(corpus_version)
    if spec is None:
        C._refuse("unknown corpus version %r (known: %s)" % (corpus_version, ", ".join(sorted(SPECS))))
    data_root = data_root or C.DATA_ROOT
    src_path = os.path.join(data_root, spec["db"])
    out_path = os.path.join(out_dir, "corpus_v2_%s.db" % spec["file_tag"])
    out("[M1] %s: source %s (read-only), output %s" % (corpus_version, src_path, out_path))
    src_sha = ro.file_sha256(src_path)
    src = ro.open_ro(src_path)
    keys = C.KeyCache()
    try:
        present = [r[0] for r in src.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        missing = [t for t in spec["tables_read"] if t not in present]
        if missing:
            C._refuse("%s lacks the declared table(s) %s" % (src_path, missing))
        # ── source rows
        srows = []
        for r in spec["source_rows"](src):
            stem_key = keys.stem(r["text"])
            vid, opts = keys.variant(r["text"], r["options_json"], r["contract"])
            at = C.answer_text(r["gt"], opts)
            srows.append({**r, "id": C.source_row_id(corpus_version, r["table"], r["upstream_pk"]),
                          "stem_key": stem_key, "item_id": C.item_id_of_key(stem_key), "variant_id": vid, "opts": opts,
                          "answer_text": at, "raw_sha256": _sha(r["raw"])})
        by_pk = {(r["table"], r["upstream_pk"]): r["id"] for r in srows}
        if len(by_pk) != len(srows) or len({r["id"] for r in srows}) != len(srows):
            C._refuse("source_row ids are not unique")
        out("[M1] %s: %d source rows read" % (corpus_version, len(srows)))
        conn = ro.create_new(out_path)
        conn.executescript(DDL)
        variants = {}
        items = {}

        def _variant(vid, item_id, contract, stem, opts, origin):
            v = variants.get(vid)
            if v is None:
                if contract not in CONTRACTS:
                    C._refuse("contract %r is not in the closed list %s (variant %s); a new contract is a code change"
                              % (contract, CONTRACTS, vid))
                v = variants[vid] = {"item_id": item_id, "contract": contract, "stem": stem,
                                     "opts": json.dumps(C.sorted_norm_options(opts), ensure_ascii=False),
                                     "answers": set(), "origin": origin, "n_src": 0, "n_resp": 0}
            elif v["item_id"] != item_id:
                C._refuse("variant %s maps to two items" % vid)
            return v

        def _item(item_id, stem_key, origin):
            it = items.get(item_id)
            if it is None:
                it = items[item_id] = {"stem_key": stem_key, "origin": origin, "variants": set(), "n_src": 0, "n_resp": 0}
            elif origin == "corpus":
                it["origin"] = "corpus"
            return it

        opt_seen = set()

        def _options(options_json):
            """Content-addressed store of the VERBATIM ordered options (one row per distinct raw options_json)."""
            sha = C.options_ordered_sha(options_json)
            if sha not in opt_seen:
                opt_seen.add(sha)
                conn.execute("INSERT INTO options_ordered VALUES (?,?,?,?)",
                             (sha, int(options_json is None), "zlib", zlib.compress((options_json or "").encode("utf-8"), 6)))
            return sha

        labels = defaultdict(Counter)
        for r in srows:
            v = _variant(r["variant_id"], r["item_id"], r["contract"], r["text"], r["opts"], "corpus")
            v["n_src"] += 1
            if r["answer_text"] is not None:
                v["answers"].add(C.split_side.norm(r["answer_text"]))
            it = _item(r["item_id"], r["stem_key"], "corpus")
            it["variants"].add(r["variant_id"]); it["n_src"] += 1
            for scheme, lab in r["labels"].items():
                if lab is not None:
                    labels[(r["item_id"], scheme)][lab] += 1
            conn.execute("INSERT INTO source_row VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (r["id"], r["table"], r["upstream_pk"], r["upstream_id"], r["source"], r["domain"], r["subset_tag"],
                          r["variant_id"], r["item_id"], r["text"], r["options_json"],
                          _options(r["options_json"]), r["gt"], r["answer_text"], r["raw_sha256"]))
        # ── responses (streamed; outputs stored zlib-compressed with their sha256)
        n_resp = 0
        model_n = Counter()
        seen_by_qid = defaultdict(Counter)       # active models: legacy qid -> stem_key counts
        quarantined_rows = defaultdict(list)     # model -> [(qid, stem_key)]
        solver_ck = {}                           # legacy qid -> seen_ck of SOLVER_MODEL's row (reference crossing)
        import hashlib
        for r in spec["responses"](src):
            stem_key = keys.stem(r["text"])
            vid, opts = keys.variant(r["text"], r["options_json"], r["contract"])
            item_id = C.item_id_of_key(stem_key)
            at = C.answer_text(r["gt"], opts)
            v = _variant(vid, item_id, r["contract"], r["text"], opts, "response")
            v["n_resp"] += 1
            if at is not None and r["model"] not in C.QUARANTINED:
                v["answers"].add(C.split_side.norm(at))
            it = _item(item_id, stem_key, "response")
            it["variants"].add(vid); it["n_resp"] += 1
            model_n[r["model"]] += 1
            if r["model"] in C.QUARANTINED:
                quarantined_rows[r["model"]].append((r["legacy_qid"], stem_key))
            else:
                seen_by_qid[r["legacy_qid"]][stem_key] += 1
                labels[(item_id, "eval_results.category")][r["category"]] += 1
            if r["model"] == SOLVER_MODEL:
                solver_ck[r["legacy_qid"]] = vid
            outb = (r["output"] or "").encode("utf-8")
            xid = C.response_id(corpus_version, r["model"], r["legacy_qid"])
            conn.execute("INSERT INTO response VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (xid, r["model"], r["legacy_qid"],
                          r["source"], vid, item_id, _options(r["options_json"]), r["gt"], at, r["pred"],
                          r["is_correct"], r["is_correct_mathfix"], r["category"],
                          hashlib.sha256(outb).hexdigest(), zlib.compress(outb, 6)))
            conn.execute("INSERT INTO retired_legacy_flag VALUES (?,?)", (xid, r["legacy_is_reserved"]))
            n_resp += 1
        out("[M1] %s: %d response rows, %d models" % (corpus_version, n_resp, len(model_n)))
        # response-only variants of QUARANTINED models carry no answer text of record (their rows are id-shifted)
        # ── aliases
        alias_rows = Counter()
        for a in spec["aliases"](src):
            ns, legacy, (table, pk) = a[0], a[1], a[2]
            seq = a[3] if len(a) > 3 else 0
            rid = by_pk.get((table, pk))
            if rid is None:
                C._refuse("alias %s:%s points to %s:%s, which is not a source row" % (ns, legacy, table, pk))
            alias_rows[(ns, legacy, "source_row", rid, seq)] += 1
        qid_variants = defaultdict(Counter)
        for (qid, model), vid in ((k, v) for k, v in _qid_variant_pairs(conn)):
            if model not in C.QUARANTINED:
                qid_variants[qid][vid] += 1
        for qid, vs in qid_variants.items():
            for vid, n in vs.items():
                alias_rows[("legacy_eval_question_id", str(qid), "variant", vid, 0)] += n
        for (ns, legacy, kind, tid, seq), n in sorted(alias_rows.items()):
            conn.execute("INSERT INTO alias VALUES (?,?,?,?,?,?)", (ns, legacy, kind, tid, seq, n))
    finally:
        src.close()
    ref_counts = _ingest_references(conn, corpus_version, data_root, repo_root, solver_ck, qid_variants,
                                    {v: d["item_id"] for v, d in variants.items()}, out)
    # ── variants, items, labels, conflicts, subsets, answer classes, models, quarantine
    for vid in sorted(variants):
        v = variants[vid]
        ans = sorted(v["answers"])
        conn.execute("INSERT INTO variant VALUES (?,?,?,?,?,?,?,?,?,?)",
                     (vid, v["item_id"], v["contract"], v["stem"], v["opts"], ans[0] if len(ans) == 1 else None, len(ans),
                      v["origin"], v["n_src"], v["n_resp"]))
    for iid in sorted(items):
        it = items[iid]
        conn.execute("INSERT INTO item VALUES (?,?,?,?,?,?,?)",
                     (iid, it["stem_key"], None, it["origin"], len(it["variants"]), it["n_src"], it["n_resp"]))
    n_conf = Counter()
    for (iid, scheme), cnt in sorted(labels.items()):
        for lab, n in sorted(cnt.items()):
            conn.execute("INSERT INTO label VALUES (?,?,?,?)", (iid, scheme, lab, n))
        if len(cnt) > 1:
            conn.execute("INSERT INTO label_conflict VALUES (?,?,?)", (iid, scheme, json.dumps(sorted(cnt), ensure_ascii=False)))
            n_conf[scheme] += 1
    text_of = {r["id"]: (r["text"], r["opts"]) for r in srows}
    target_of = {r["id"]: r["answer_text"] for r in srows}
    groups = C.cc.label_conflicts([r["id"] for r in srows], text_of, target_of)
    for g in groups:
        conn.execute("INSERT INTO answer_class VALUES (?,?,?,?)",
                     ("i:" + g["key"], g["class"], json.dumps(g["targets"], ensure_ascii=False), json.dumps(g["ids"])))
    classes = C.cc.label_classes(groups)
    gp = [r for r in srows if r["source"] in SUBSET_SOURCES]
    n_gpqa_items = None
    if gp:
        rows1 = C.cc.one_row_per_key([r["id"] for r in gp], text_of, {r["id"]: r["subset_tag"] for r in gp})
        n_gpqa_items = len(rows1)
        for k, v in rows1.items():
            for tag in v["tags"]:
                conn.execute("INSERT INTO item_subset VALUES (?,?,?)", ("i:" + k, tag, v["row"]))
    for m in sorted(model_n):
        st = "QUARANTINED" if m in C.QUARANTINED else "ACTIVE"
        conn.execute("INSERT INTO model_registry VALUES (?,?,?,?)", (m, st, C.QUARANTINED.get(m), model_n[m]))
    qdef = ("among the rows whose legacy question_id also has ACTIVE-model rows: those whose own stem_key differs from the"
            " modal stem_key of the active rows of that qid; rows of a qid with no active row are counted apart"
            " (n_no_active_row)")
    qc = {}
    for m, rows in sorted(quarantined_rows.items()):
        mis = no = 0
        for qid, k in rows:
            modal = seen_by_qid.get(qid)
            if not modal:
                no += 1
            elif k != sorted(modal.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]:
                mis += 1
        conn.execute("INSERT INTO quarantine_check VALUES (?,?,?,?,?)", (m, len(rows), mis, no, qdef))
        qc[m] = (len(rows), mis, no)
    n_items_corpus = sum(1 for it in items.values() if it["origin"] == "corpus")
    meta = {
        "corpus_version": corpus_version, "source_db": spec["db"], "source_db_sha256_bytes": src_sha,
        "tables_read": json.dumps(spec["tables_read"]), "excluded_tables": json.dumps(spec["excluded_tables"]),
        "normaliser": C.split_side.NORMALISER_VERSION, "key_rule": C.split_side.KEY_RULE,
        "option_extractor": C.OPTION_EXTRACTOR, "content_closure_blob": C.PINS["content_closure"],
        "split_side_blob": C.PINS["split_side"], "data_v2_ingest_blob": ro.git_blob_lf(os.path.abspath(__file__)),
        "quarantine_definition": qdef, "domain_scheme": spec["domain_scheme"], "contracts": json.dumps(CONTRACTS),
        "reference_solver_model": SOLVER_MODEL,
        "reference_crossing": "solver_row (legacy qid + solver model -> seen_ck) | unique_active_variant | unresolved",
        "retired_columns": "legacy_is_reserved -> retired_legacy_flag only (never read by v2 split / view code)",
        "response_domain_scheme": "eval_results.category",
    }
    for k in sorted(meta):
        conn.execute("INSERT INTO meta VALUES (?,?)", (k, str(meta[k])))
    conn.commit()
    counts = {"source_rows": len(srows), "items": len(items), "items_corpus": n_items_corpus,
              "items_response_only": len(items) - n_items_corpus, "variants": len(variants),
              "variants_response_only": sum(1 for v in variants.values() if v["origin"] == "response"),
              "variants_answer_conflict": sum(1 for v in variants.values() if len(v["answers"]) > 1),
              "responses": n_resp, "models": len(model_n), "label_conflicts": dict(n_conf), "answer_classes": classes,
              "gpqa_items": n_gpqa_items, "references": ref_counts, "options_ordered_rows": len(opt_seen),
              "quarantine": {m: {"rows": a, "content_mismatch": b, "no_active_row": c}
                                                          for m, (a, b, c) in qc.items()}}
    out("[M1] %s: items %d (corpus %d, response-only %d), variants %d (response-only %d, answer conflict %d)"
        % (corpus_version, counts["items"], counts["items_corpus"], counts["items_response_only"], counts["variants"],
           counts["variants_response_only"], counts["variants_answer_conflict"]))
    out("[M1] %s: label conflicts by scheme %s; answer classes %s; GPQA items %s"
        % (corpus_version, json.dumps(dict(sorted(n_conf.items()))), json.dumps(classes), n_gpqa_items))
    for m, (a, b, c) in qc.items():
        rec = QUARANTINE_RECORD.get((corpus_version, m))
        verdict = "" if rec is None else (" record %d of %d: %s" % (rec[0], rec[1], "MATCH" if (b, a) == rec else "MISMATCH"))
        out("[M1] %s: QUARANTINED %s: %d rows; %d of the %d with an active row of their qid carry another stem than the"
            " active modal stem; %d rows have no active row;%s" % (corpus_version, m, a, b, a - c, c, verdict))
    sealed = ro.seal(conn, out_path, "corpus_v2 %s" % corpus_version)
    out("[M1] %s: SEALED %s sha256-bytes %s" % (corpus_version, os.path.basename(out_path), sealed["sha256_bytes"]))
    return {"path": out_path, "kind": "corpus_v2", "corpus_version": corpus_version, "counts": counts,
            "record": spec["record"], "source_db": spec["db"], "source_db_sha256_bytes": src_sha, **sealed}


def _ingest_references(conn, corpus_version, data_root, repo_root, solver_ck, qid_variants, variant_item, out):
    """Legacy reference vintages -> `reference` (keyed by variant_id) or `reference_unresolved`. Read-only on the caches;
    a declared cache that is missing is REFUSED (fail closed). Returns {vintage: {resolution: n}}."""
    counts = {}
    for spec in LEGACY_REFERENCES.get(corpus_version, ()):
        path = os.path.join(data_root, spec["db"])
        sha = ro.file_sha256(path)
        listed = None
        if spec["side_pool_file"]:
            with open(os.path.join(repo_root, spec["side_pool_file"]), "r", encoding="utf-8") as f:
                ids = json.load(f)
            listed = {q for v in ids.values() for q in v if q > 0}
        rc = ro.open_ro(path)
        try:
            cols = [r[1] for r in rc.execute("PRAGMA table_info(answers)")]
            if "question_id" not in cols:
                C._refuse("%s: table answers has no question_id" % path)
            has_side = "side_at_mint" in cols
            take = [c for c in REFERENCE_COLS if c in cols]
            sel =["question_id"] + take + (["side_at_mint"] if has_side else []) + (["ts"] if "ts" in cols else [])
            rows = rc.execute("SELECT %s FROM answers ORDER BY question_id" % ", ".join(sel)).fetchall()
        finally:
            rc.close()
        n = Counter()
        for row in rows:
            d = dict(zip(sel, row))
            q = d["question_id"]
            key = "qid:%d" % q
            if q in solver_ck:
                vid, how = solver_ck[q], "solver_row"
            elif len(qid_variants.get(q, {})) == 1:
                vid, how = next(iter(qid_variants[q])), "unique_active_variant"
            else:
                cands = sorted(qid_variants.get(q, {}))
                conn.execute("INSERT INTO reference_unresolved VALUES (?,?,?,?,?,?,?,?)",
                             (spec["vintage"], key, q, "no %s row and %d active variants" % (SOLVER_MODEL, len(cands)),
                              json.dumps(cands), d.get("answer"), d.get("raw"), spec["db"]))
                n["unresolved"] += 1
                continue
            if has_side:
                side, rule = str(d["side_at_mint"]), "copied from the cache's side_at_mint column"
            elif listed is not None:
                side = "EVAL" if q in listed else "NOT_LISTED"
                rule = "derived: listed judgeable id of %s (id-only) at mint time" % spec["side_pool_id"]
            else:
                C._refuse("%s: no side_at_mint column and no pool file to derive it" % path)
            minted = d.get("minted_at")
            if minted is None and d.get("ts") is not None:
                from datetime import datetime, timezone
                minted = datetime.fromtimestamp(float(d["ts"]), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            vals = [d.get(c) for c in REFERENCE_COLS]
            vals[REFERENCE_COLS.index("minted_at")] = minted
            conn.execute("INSERT INTO reference VALUES (%s)" % ",".join("?" * (10 + len(REFERENCE_COLS))),
                         (vid, spec["vintage"], key, variant_item[vid], q, side, rule, how, *vals, spec["db"], sha))
            n[how] += 1
        counts[spec["vintage"]] = dict(n)
        out("[M1] %s: legacy references %s (%s, sha256-bytes %s): %d rows -> %s"
            % (corpus_version, spec["vintage"], spec["db"], sha[:16], len(rows), json.dumps(dict(sorted(n.items())))))
    return counts


def _qid_variant_pairs(conn):
    for qid, model, vid in conn.execute("SELECT legacy_qid, model, seen_ck FROM response ORDER BY legacy_qid, model"):
        yield (qid, model), vid
