"""MMLU-GOLD-GEOMETRY: is MMLU-Pro's declared 14-category level a geometric level over its fine sources in qwen3?

REGISTRATION: docs/judge_v2_program.md section "## Registered 2026-10-01 (before any code or call) — MMLU-GOLD-GEOMETRY: over
MMLU-Pro's fine sources (src x category), does the declared 14-category level form geometric clusters in qwen3 (H above its
permutation p95), and where does it sit beside CLINC 0.143 and MASSIVE 0.404 (descriptive)? ..." (span L22332-L22357, _as_of
b909414, the registrar's commit). Kind zero-call (R-4). It must run, with its outcome recorded, BEFORE RP12's G12 is read (B-A2;
R-3).

WHAT IT COMPUTES. S0's D2 function VERBATIM: tools/analysis/intent_transfer_s0.py blob:f662ceb19738f515972871f5963f5dcfc764a271
is imported unchanged (its LF blob is asserted at import; any other blob REFUSES) and its d2(C, S) is called on a Corpus of the
MMLU_PRO_LB member's TRAIN items: average-link (cosine) on the 91 gold fine TRAIN centroids, cut at K_c = 14, ARI against the gold
fine -> coarse map; null = 1,000 size-matched random relabellings (permutations of the gold map), p95. qwen3 slice 256 decides
(S0's D2 slice); slice 512 printed. An item bootstrap (items resampled WITHIN each fine label, B 1,000) prints a CI that never
decides.
  G-1 (the POINT decides): HELD iff H > p95; FAILED iff H <= p95. No UNDETERMINED. F-G1 fires iff G-1 FAILED.
  Prediction H 0.30 [0.12, 0.50] (80%) scored HELD iff the point lies in the closed interval; G-1 HELD p 0.85 with its Brier.

DATA (the data-steward's precondition, re-implemented from scratchpad/src_census.py, not imported):
  * fine label = doc.src of the raw Open-LLM-Leaderboard MMLU-Pro sample files (experiment_results/multicorpus/raw/*/*/
    samples_leaderboard_mmlu_pro_*.jsonl); the first RAW_N = 3 files (sorted by path) are read and must agree (qid -> src,
    category, options key); a disagreement REFUSES.
  * JOIN BY THE OPTIONS KEY, NEVER BY TEXT: key = json.dumps([o.strip() for o in options], ensure_ascii=False); the DB side is
    corpus_questions.options_json through data_v2.common.extract_options. A row whose key hits no raw doc is UNMATCHED; a key
    hitting docs of >= 2 distinct src is AMBIGUOUS; both are excluded and printed by count (R-2). Beside it (descriptive only):
    how many matched rows carry upstream_id == the matched doc's question_id.
  * the member (R-1): MMLU_PRO_LB on the multi-corpus route = corpus_questions rows with source 'MMLU_PRO' of
    multicorpus_cache_v1.db; item = 'i:' + split_side.stem_key(text) (blank texts skipped, counted); side from the committed side
    export of draw 5a3e756 (data_v2/manifests/REG_ARCHV2-SPLIT-2_..._side.tsv, verified by v2_engine_pool.read_side, pinned by
    sha256 of its LF rendering); TRAIN = side TRAIN and tagged mc6-2026-09-11. The TRAIN item count must equal 6,992 (the
    data-steward's [ITEM-CENSUS] bracket, prog L22242-L22250); otherwise REFUSES (a failed precondition).
  * an item's src = the src of its matched rows; an item with rows of >= 2 src (multi-src) or >= 2 domains is excluded
    (counted); coarse = the corpus row's domain (the declared category); the raw category disagreeing with it is counted.
    Nesting: a src under >= 2 categories REFUSES. Labels: exactly 91 fine labels in exactly 14 categories, each label >= 10
    TRAIN items and each category >= 2 labels, else REFUSES (the registration's ">= 2 required, else declined").
  * the item's text = its smallest-question_id row's text (rp12_pairing P4); its vector = embeddings_cache.db (qwen3 of record,
    4096-d big-endian float32, keyed by text); a missing or non-4096 vector REFUSES.
  * EVAL: never a vector, never a label count of record; ONLY the count of EVAL items whose options key finds no src is printed
    (the 13 of 3,492 disclosed; R-2). GATE is not read beyond its side.

HYGIENE. A RULE-7 READER: --dry-run and --run REFUSE while a java.exe (a construction or site null) runs. embeddings_cache.db and
multicorpus_cache_v1.db are opened mode=ro&immutable=1 after the sidecar check; the per-table hashes of embeddings_cache.db and the
table hash of corpus_questions are printed before and after the readout and a change REFUSES (nothing written). Every fit goes
through S0's fit_rows (TRAIN-ONLY audit printed). No pool guard (registered: the pv2 pool check is not engaged, no EVAL read).
No judge, no cap, no temperature, no cache, zero calls. Threads: OMP/OPENBLAS/MKL = 1.

OUTPUT. experiment_results/mmlu_gold_geometry/outcome.txt, WRITE-ONCE (opened with mode "x"; an existing path REFUSES before any
read). --dry-run writes nothing and computes no H.

BUILDER'S READINGS (points the registered text leaves open; printed in the outcome; the registrar confirms or brackets):
  GB1 d2's null seed: S0's d2 seeds its null with SEED_D2 + CORPORA.index(C.name); this script registers the member as a fourth
      corpus name 'mmlu_pro_lb' for the call only (II.GOLD_K['mmlu_pro_lb'] = (14, 91), ITS.CORPORA + ('mmlu_pro_lb',), both
      restored after), so the seed is SEED_D2 + 3 = 2105. The function body is untouched.
  GB2 fine label = src alone (the census found every src under exactly one category, so src == (src, category)); the nesting
      check enforces it.
  GB3 the null SD, null mean and MDE80 are MEASURED from the same 1,000 permutations (a replica of d2's null with the same seed,
      whose p95 must equal d2's exactly, else REFUSES); the transported 0.018 / 0.045 are printed beside.
  GB4 the item bootstrap uses seed BOOT_SEED = 20261001 and percentile 95% limits.

LAUNCH (run-operator; zero calls; no construction or site null running; ONE heavy process):
  python tools/analysis/mmlu_gold_geometry.py --selftest
  python tools/analysis/mmlu_gold_geometry.py --mutants
  python tools/analysis/mmlu_gold_geometry.py --dry-run     # counts, joins, labels, vector presence; no H; nothing written
  python tools/analysis/mmlu_gold_geometry.py --run         # the file of record (write-once)
  (DBs and raw files are read under TAXOARENA_DATA_ROOT, default the repo root; --db / --emb-db / --raw-glob override.)

SELFTEST MUTANTS: the table MUTANTS below is executed by --mutants (each a temporary source edit run against the selftest
sections named beside it; the harness reports KILLED / SURVIVED). The run of record is in the commit message.
"""
import os

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import argparse        # noqa: E402
import contextlib      # noqa: E402
import glob            # noqa: E402
import hashlib         # noqa: E402
import io              # noqa: E402
import json            # noqa: E402
import sqlite3         # noqa: E402
import sys             # noqa: E402
import tempfile        # noqa: E402

import numpy as np     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import intent_transfer_s0 as ITS      # noqa: E402  (S0's D2, imported unchanged; blob asserted below)
import v2_engine_pool as EP           # noqa: E402  (read_side: the side export's verification)
import split_side as SS               # noqa: E402
from data_v2 import ro as RO          # noqa: E402
from data_v2 import common as DC      # noqa: E402

II = ITS.II
TAG = "[GOLD-GEOM]"
ITS_BLOB = "f662ceb19738f515972871f5963f5dcfc764a271"
NAME = "mmlu_pro_lb"
K_C, K_F = 14, 91
MIN_ITEMS, MIN_FINE_PER_CAT = 10, 2
EXPECT_TRAIN_ITEMS = 6992
SLICE, SLICE2 = ITS.SLICE, ITS.SLICE2
NATIVE_DIM = 4096
D2_REPS = ITS.D2_REPS
BOOT_B, BOOT_SEED = 1000, 20261001
H_BESIDE = (("CLINC qwen3", 0.1429), ("MASSIVE qwen3", 0.4040))
PRED_H, PRED_P = (0.30, 0.12, 0.50), 0.85
NULL_SD_TRANSPORTED, MDE_TRANSPORTED = 0.018, 0.045
Z_MDE = 1.645 + 0.84
SOURCE, CORPUS_TAG = "MMLU_PRO", "mc6-2026-09-11"
SIDE_FILE = os.path.join(ROOT, EP.DEFAULT_SIDE)
SIDE_SHA_LF = "47e9048bb09a6910a2d511cf3c3f4d8ba734ef44ca78c87f7a60a9fc99cc4764"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
DB_FILE = os.path.join(DATA_ROOT, "multicorpus_cache_v1.db")
EMB_FILE = os.path.join(DATA_ROOT, "embeddings_cache.db")
RAW_GLOB = os.path.join(DATA_ROOT, "experiment_results", "multicorpus", "raw", "*", "*", "samples_leaderboard_mmlu_pro_*.jsonl")
RAW_N = 3
OUT_FILE = os.path.join(ROOT, "experiment_results", "mmlu_gold_geometry", "outcome.txt")
REG = ('docs/judge_v2_program.md "## Registered 2026-10-01 (before any code or call) — MMLU-GOLD-GEOMETRY: ..." L22332-L22357 '
       '_as_of b909414; kind zero-call (R-4)')


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def check_its_blob():
    got = RO.git_blob_lf(ITS.__file__)
    if got != ITS_BLOB:
        refuse("intent_transfer_s0.py is blob %s, not the registered %s: D2 must be imported unchanged" % (got, ITS_BLOB))
    return got


_foreign_heavy = ITS._foreign_heavy


def heavy_check():
    heavy = _foreign_heavy()
    print("%s heavy foreign processes: %s" % (TAG, heavy if heavy else "none"))
    if heavy:
        refuse("a foreign heavy process runs (%s): this is a rule-7 reader of embeddings_cache.db; never beside a construction "
               "or site null" % heavy[:3])


# ------------------------------------------------------------------------------------------------ inputs
def okey(opts):
    return json.dumps([o.strip() for o in opts], ensure_ascii=False)


def read_raw(files):
    """-> {qid: (src, category, options key)} of the first file; REFUSES unless every file agrees."""
    if not files:
        refuse("no raw MMLU-Pro leaderboard sample file found")
    per = []
    for f in files:
        d = {}
        with open(f, encoding="utf-8") as fh:
            for ln in fh:
                if not ln.strip():
                    continue
                doc = json.loads(ln)["doc"]
                d[int(doc["question_id"])] = (doc["src"], doc["category"], okey(doc["options"]))
        per.append(d)
        print("%s raw %s: %d docs" % (TAG, os.path.basename(f), len(d)))
    if any(p != per[0] for p in per[1:]):
        refuse("the %d raw files disagree on qid -> (src, category, options)" % len(per))
    return per[0]


def raw_index(raw):
    byk = {}
    for qid, (s, cat, k) in raw.items():
        byk.setdefault(k, set()).add((s, cat, qid))
    return byk


def read_rows(db):
    con = RO.open_ro(db)
    try:
        return con.execute("SELECT question_id, upstream_id, text, domain, options_json FROM corpus_questions WHERE source = ? "
                           "ORDER BY question_id", (SOURCE,)).fetchall()
    finally:
        con.close()


def corpus_table_sha(db):
    con = RO.open_ro(db)
    try:
        s, n = RO.table_sha(con, "corpus_questions")
        return "%s/%d" % (s[:16], n)
    finally:
        con.close()


def emb_table_hashes(path):
    con = RO.open_ro(path)
    try:
        return {t: v["table_sha"][:16] + "/%d" % v["rows"] for t, v in RO.table_shas(con).items()}
    finally:
        con.close()


def member(rows, side_items, byk):
    """-> dict with the TRAIN items (src, domain, text), and every count printed."""
    keys = DC.KeyCache()
    cnt = {"rows": len(rows), "blank": 0, "no_side": 0, "not_tagged": 0, "train_rows": 0, "eval_rows": 0, "gate_rows": 0,
           "train_matched": 0, "train_unmatched": 0, "train_ambiguous": 0, "upstream_agree": 0, "cat_mismatch": 0}
    tr, ev = {}, {}
    for qid, up, text, dom, opts in rows:
        if text is None or EP._kotlin_blank(text):
            cnt["blank"] += 1
            continue
        it = "i:" + keys.stem(text)
        si = side_items.get(it)
        if si is None:
            cnt["no_side"] += 1
            continue
        _comp, side, corpora = si
        if CORPUS_TAG not in corpora:
            cnt["not_tagged"] += 1
            continue
        hits = byk.get(okey(DC.extract_options(opts)), set())
        srcs = {h[0] for h in hits}
        if side == "EVAL":
            cnt["eval_rows"] += 1
            ev.setdefault(it, set()).update(srcs if len(srcs) == 1 else ())
            continue
        if side != "TRAIN":
            cnt["gate_rows"] += 1
            continue
        cnt["train_rows"] += 1
        e = tr.setdefault(it, {"rows": [], "src": set(), "dom": set(), "comp": _comp})
        e["rows"].append((qid, text))
        e["dom"].add(dom)
        if not srcs:
            cnt["train_unmatched"] += 1
        elif len(srcs) > 1:
            cnt["train_ambiguous"] += 1
        else:
            cnt["train_matched"] += 1
            s, cat, _q = sorted(hits)[0]
            e["src"].add(s)
            cnt["upstream_agree"] += int(any(int(up) == h[2] for h in hits))
            cnt["cat_mismatch"] += int(cat != dom)
    cnt["train_texts"] = len({t for e in tr.values() for _q, t in e["rows"]})
    cnt["train_items"] = len(tr)
    cnt["eval_items"] = len(ev)
    cnt["eval_no_src"] = sum(1 for v in ev.values() if not v)
    kept, ex = {}, {"no_src": 0, "multi_src": 0, "multi_dom": 0}
    for it, e in sorted(tr.items()):
        if not e["src"]:
            ex["no_src"] += 1
            continue
        if len(e["src"]) > 1:
            ex["multi_src"] += 1
            continue
        if len(e["dom"]) > 1:
            ex["multi_dom"] += 1
            continue
        qid, text = min(e["rows"])
        kept[it] = {"src": next(iter(e["src"])), "dom": next(iter(e["dom"])), "text": text, "comp": e["comp"]}
    return kept, cnt, ex


def label_census(kept):
    src_dom = {}
    for v in kept.values():
        src_dom.setdefault(v["src"], set()).add(v["dom"])
    bad = {s: sorted(d) for s, d in src_dom.items() if len(d) > 1}
    if bad:
        refuse("nesting: %d src values sit under >= 2 categories (first %s)" % (len(bad), sorted(bad.items())[:3]))
    n_src = {}
    for v in kept.values():
        n_src[v["src"]] = n_src.get(v["src"], 0) + 1
    per_cat = {}
    for s, d in src_dom.items():
        c = next(iter(d))
        per_cat[c] = per_cat.get(c, 0) + 1
    small = sorted((n, s) for s, n in n_src.items() if n < MIN_ITEMS)
    if len(n_src) != K_F:
        refuse("%d fine labels, not the registered %d" % (len(n_src), K_F))
    if len(per_cat) != K_C:
        refuse("%d categories, not the registered %d" % (len(per_cat), K_C))
    if small:
        refuse("%d fine labels hold < %d TRAIN items (first %s)" % (len(small), MIN_ITEMS, small[:3]))
    thin = sorted(c for c, n in per_cat.items() if n < MIN_FINE_PER_CAT)
    if thin:
        refuse("categories with < %d fine labels (declined): %s" % (MIN_FINE_PER_CAT, thin))
    v = sorted(n_src.values())
    return {"n_fine": len(n_src), "n_cat": len(per_cat), "min": v[0], "median": float(np.median(v)), "max": v[-1],
            "per_cat": dict(sorted(per_cat.items())), "mean_per_cat": len(n_src) / float(len(per_cat))}


def assignment_digest(kept):
    h = hashlib.sha256()
    for it in sorted(kept):
        h.update(("%s\t%s\t%s\n" % (it, kept[it]["src"], kept[it]["dom"])).encode("utf-8"))
    return h.hexdigest()[:16]


def text_digest(kept):
    h = hashlib.sha256()
    for it in sorted(kept):
        h.update(("%s\t%s\n" % (it, kept[it]["text"])).encode("utf-8"))
    return h.hexdigest()[:16]


def load_vectors(path, texts):
    want = sorted(set(texts))
    out, dims = {}, {}
    con = RO.open_ro(path)
    try:
        for s in range(0, len(want), 500):
            ch = want[s:s + 500]
            for t, b in con.execute("SELECT query, vector FROM embeddings WHERE query IN (%s)" % ",".join("?" * len(ch)), ch):
                n = len(b) // 4 if isinstance(b, (bytes, bytearray)) else -1
                dims[n] = dims.get(n, 0) + 1
                if n == NATIVE_DIM:
                    out[t] = np.frombuffer(b, dtype=">f4", count=SLICE2).astype(np.float64)
    finally:
        con.close()
    print("%s vectors: %d of %d item texts have a %d-d vector (dims seen %s)" % (TAG, len(out), len(want), NATIVE_DIM,
                                                                              dict(sorted(dims.items()))))
    if set(dims) - {NATIVE_DIM}:
        refuse("vector dims %s != {%d}" % (sorted(dims), NATIVE_DIM))
    if len(out) != len(want):
        refuse("%d item texts have no vector in %s" % (len(want) - len(out), path))
    return out


def corpus_of(kept):
    rows = [{"item_id": it, "text": v["text"], "coarse": v["dom"], "fine": v["src"], "side": SS.TRAIN, "hash_side": SS.TRAIN,
             "is_oos": 0, "drop_reason": None, "stem_key": it[2:], "annot": None} for it, v in kept.items()]
    return ITS.Corpus(NAME, rows)


@contextlib.contextmanager
def s0_slot():
    """GB1: the member enters S0's d2 as a fourth corpus name for the call only; both module globals restored after."""
    had, saved_k, saved_c = NAME in II.GOLD_K, II.GOLD_K.get(NAME), ITS.CORPORA
    II.GOLD_K[NAME] = (K_C, K_F)
    ITS.CORPORA = tuple(saved_c) + (NAME,)
    try:
        yield
    finally:
        ITS.CORPORA = saved_c
        if had:
            II.GOLD_K[NAME] = saved_k
        else:
            II.GOLD_K.pop(NAME, None)


# ------------------------------------------------------------------------------------------------ statistics
def h_point(X, fine, coarse, kc=K_C):
    """The H of S0's d2 restated for the bootstrap (asserted equal to d2's H on the full data)."""
    from scipy.cluster.hierarchy import linkage, fcluster
    u, G = ITS.centroids_by_label(X, fine)
    f2c = dict(zip(fine.tolist(), coarse.tolist()))
    gold = ITS.codes([f2c[x] for x in u])
    cut = fcluster(linkage(G, method="average", metric="cosine"), t=kc, criterion="maxclust")
    return ITS.ari(gold, cut)


def null_replica(C, S):
    tr = ITS.fit_rows(C, ITS.S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "GOLD-GEOM null replica centroids")
    u, _G = ITS.centroids_by_label(S.X[tr], C.fine[tr])
    f2c = {}
    for i in tr:
        f2c[C.fine[i]] = C.coarse[i]
    gold = ITS.codes([f2c[x] for x in u])
    rng = np.random.default_rng(ITS.SEED_D2 + ITS.CORPORA.index(C.name))
    null = np.array([ITS.ari(gold, rng.permutation(gold)) for _ in range(D2_REPS)])
    return {"p95": float(np.percentile(null, 95)), "mean": float(null.mean()), "sd": float(null.std(ddof=1))}


def resample_within(groups, rng):
    """One bootstrap draw: each fine label's items resampled with replacement WITHIN the label (its count kept)."""
    return np.concatenate([g[rng.integers(len(g), size=len(g))] for g in groups])


def item_bootstrap(C, S, B=BOOT_B, seed=BOOT_SEED):
    tr = ITS.fit_rows(C, ITS.S_idx(C, S, SS.TRAIN), (SS.TRAIN,), "GOLD-GEOM item bootstrap (resamples these rows only)")
    by = {}
    for i in tr:
        by.setdefault(C.fine[i], []).append(int(i))
    groups = [np.array(by[k]) for k in sorted(by)]
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B):
        idx = resample_within(groups, rng)
        draws.append(h_point(S.X[idx], C.fine[idx], C.coarse[idx]))
    d = np.array(draws)
    return {"lo": float(np.percentile(d, 2.5)), "hi": float(np.percentile(d, 97.5)), "se": float(d.std(ddof=1)), "B": B}


def geometry(C, vecs, slice_):
    S = ITS.Space(vecs, C, slice_)
    with s0_slot():
        r = ITS.d2(C, S)
        rep = null_replica(C, S)
    tr = ITS.S_idx(C, S, SS.TRAIN)
    hp = h_point(S.X[tr], C.fine[tr], C.coarse[tr])
    if hp != r["H"] or rep["p95"] != r["p95"]:
        refuse("the replica disagrees with S0's d2 (H %r vs %r; p95 %r vs %r)" % (hp, r["H"], rep["p95"], r["p95"]))
    r.update(null_mean=rep["mean"], null_sd=rep["sd"])
    return r, S


def g1_verdict(H, p95):
    return "HELD" if bool(float(H) > float(p95)) else "FAILED"


def in_interval(v, lo, hi):
    return "HELD" if bool(lo <= float(v) <= hi) else "FAILED"


def brier(p, event):
    return (float(p) - (1.0 if bool(event) else 0.0)) ** 2


# ------------------------------------------------------------------------------------------------ readout
def assemble(db, emb, side_path, raw_files, expect_items=EXPECT_TRAIN_ITEMS, side_sha=SIDE_SHA_LF):
    side_items, smeta = EP.read_side(side_path)
    print("%s side export %s: sha256-lf %s [%s]; split_sha256 %s; rows %d" % (
        TAG, smeta["path"], smeta["sha256_lf"], "PIN OK" if smeta["sha256_lf"] == side_sha else "PIN MISMATCH",
        smeta["split_sha256"], smeta["rows"]))
    if smeta["sha256_lf"] != side_sha:
        refuse("the side export's LF sha256 %s != the pinned %s" % (smeta["sha256_lf"], side_sha))
    raw = read_raw(raw_files)
    byk = raw_index(raw)
    kept, cnt, ex = member(read_rows(db), side_items, byk)
    L = ["member MMLU_PRO_LB (corpus_questions source %s, tagged %s; R-1): rows %d; TRAIN rows %d -> %d texts -> %d items; "
         "EVAL rows %d / items %d; GATE rows %d; blank %d; no side %d; not tagged %d"
         % (SOURCE, CORPUS_TAG, cnt["rows"], cnt["train_rows"], cnt["train_texts"], cnt["train_items"], cnt["eval_rows"],
            cnt["eval_items"], cnt["gate_rows"], cnt["blank"], cnt["no_side"], cnt["not_tagged"]),
         "options-key join (never text) on TRAIN rows: matched %d, unmatched %d, ambiguous %d (R-2: excluded, by count); "
         "upstream_id == matched doc question_id on %d of %d matched rows (descriptive); raw category != DB domain on %d"
         % (cnt["train_matched"], cnt["train_unmatched"], cnt["train_ambiguous"], cnt["upstream_agree"], cnt["train_matched"],
            cnt["cat_mismatch"]),
         "TRAIN items excluded: no src %d, multi-src %d, multi-domain %d; kept %d (assignment digest %s; text digest %s)"
         % (ex["no_src"], ex["multi_src"], ex["multi_dom"], len(kept), assignment_digest(kept), text_digest(kept)),
         "EVAL items without src: %d of %d (disclosed and excluded; a count only, no EVAL vector or label is read; R-2)"
         % (cnt["eval_no_src"], cnt["eval_items"])]
    for ln in L:
        print("%s %s" % (TAG, ln))
    if cnt["train_items"] != expect_items:
        refuse("TRAIN items %d != %d (the data-steward's [ITEM-CENSUS] bracket): a different member" % (cnt["train_items"], expect_items))
    lab = label_census(kept)
    L.append("labels: %d fine (src) in %d categories (%.1f per category); TRAIN items per label min %d / median %.1f / max %d; "
             "per category %s" % (lab["n_fine"], lab["n_cat"], lab["mean_per_cat"], lab["min"], lab["median"], lab["max"],
                                  lab["per_cat"]))
    print("%s %s" % (TAG, L[-1]))
    return kept, L, smeta


def support_lines(lab_line_items, null_sd=None):
    L = ["SUPPORT (a) deciding unit: the fine label, K_f %d in K_c %d; items enter only through the TRAIN centroids (%d kept TRAIN "
         "items). (b) DEFF: not applicable (permutation over labels). (c) n_eff: %d labels." % (K_F, K_C, lab_line_items, K_F)]
    if null_sd is None:
        L.append("SUPPORT (d)-(e) transported: null SD %.3f, MDE80 %.3f above the null mean (measured at --run)"
                 % (NULL_SD_TRANSPORTED, MDE_TRANSPORTED))
    else:
        L.append("SUPPORT (d)-(e) MEASURED: null SD %.4f, MDE80 = %.3f x SD = %.4f above the null mean (transported: SD %.3f, "
                 "MDE80 %.3f)" % (null_sd, Z_MDE, Z_MDE * null_sd, NULL_SD_TRANSPORTED, MDE_TRANSPORTED))
    return L


def readout(C, vecs):
    del ITS.FIT_LOG[:]
    r, S = geometry(C, vecs, SLICE)
    r512, _S5 = geometry(C, vecs, SLICE2)
    bs = item_bootstrap(C, S)
    return {"r": r, "r512": r512, "bs": bs, "audit": ITS.fit_audit()}


def verdict_lines(R):
    r, r512, bs = R["r"], R["r512"], R["bs"]
    g1 = g1_verdict(r["H"], r["p95"])
    held = g1 == "HELD"
    L = ["READOUT H (qwen3 slice %d, deciding) = %.4f; random p95 = %.4f (null mean %.4f, SD %.4f, %d permutations); %d fine "
         "labels cut at K_c %d into %d clusters" % (SLICE, r["H"], r["p95"], r["null_mean"], r["null_sd"], D2_REPS, r["n_fine"],
                                                     r["k_c"], r["clusters"]),
         "READOUT item bootstrap (within fine labels, B %d; printed, never deciding): 95%% [%.4f, %.4f], SE %.4f"
         % (bs["B"], bs["lo"], bs["hi"], bs["se"]),
         "READOUT slice %d (printed, never deciding): H %.4f, p95 %.4f" % (SLICE2, r512["H"], r512["p95"]),
         "BESIDE (DESCRIPTIVE-ONLY; different K, no interval): " + "; ".join("%s H %.4f" % (n, v) for n, v in H_BESIDE)
         + "; MMLU-Pro qwen3 H %.4f" % r["H"],
         "G-1: %s (H %.4f %s p95 %.4f; the point decides)" % (g1, r["H"], ">" if held else "<=", r["p95"])]
    if held:
        L.append("F-G1: NOT FIRED")
    else:
        L.append("F-G1: FIRED (the declared categories are not a geometric level in the embedder of record; G12 is read under "
                 "B-A2: \"the declared depth-1 boundary is not shown to be geometric\")")
    L.append("PREDICTION H %.2f [%.2f, %.2f] (80%%): %s (H %.4f)" % (PRED_H + (in_interval(r["H"], PRED_H[1], PRED_H[2]), r["H"])))
    L.append("PREDICTION G-1 HELD p %.2f: event %s, Brier %.4f" % (PRED_P, g1, brier(PRED_P, held)))
    return L, g1


def header(smeta):
    return ["MMLU-GOLD-GEOMETRY outcome (tools/analysis/mmlu_gold_geometry.py, blob %s; S0 D2 from intent_transfer_s0.py blob %s, "
            "imported unchanged)" % (RO.git_blob_lf(os.path.abspath(__file__)), ITS_BLOB),
            "registration: " + REG,
            "zero calls; no construction; pool guard: none (registered: no EVAL read); split draw 5a3e756 side export sha256-lf %s"
            % smeta["sha256_lf"],
            "builder's readings: GB1 d2 null seed SEED_D2 + 3 (member as a fourth corpus name for the call only); GB2 fine = src "
            "(nesting enforced); GB3 null SD / MDE measured from the same permutations (replica p95 == d2 p95 asserted); GB4 "
            "bootstrap seed %d, percentile limits" % BOOT_SEED]


DOES_NOT_SHOW = ("DOES NOT SHOW: anything about EVAL, a tree, filing or certification (TRAIN centroids only); that the 14 categories "
                 "are the right taxonomy (H is the declared hierarchy's geometry); any non-qwen3 embedder; a comparison with CLINC "
                 "or MASSIVE beyond description (different K)")


def dry_run(db=DB_FILE, emb=EMB_FILE, side_path=SIDE_FILE, raw_files=None, expect_items=EXPECT_TRAIN_ITEMS, side_sha=SIDE_SHA_LF):
    print("%s pool guard: none (registered); zero calls; DRY RUN: nothing written, no H computed" % TAG)
    check_its_blob()
    heavy_check()
    raw_files = sorted(glob.glob(RAW_GLOB))[:RAW_N] if raw_files is None else raw_files
    kept, L, smeta = assemble(db, emb, side_path, raw_files, expect_items, side_sha)
    load_vectors(emb, [v["text"] for v in kept.values()])
    for ln in support_lines(len(kept)):
        print("%s %s" % (TAG, ln))
    print("%s DRY RUN complete: %d TRAIN items, %d fine labels; nothing written" % (TAG, len(kept), K_F))
    return 0


def main_run(db=DB_FILE, emb=EMB_FILE, side_path=SIDE_FILE, raw_files=None, out=OUT_FILE, expect_items=EXPECT_TRAIN_ITEMS,
             side_sha=SIDE_SHA_LF):
    print("%s pool guard: none (registered); zero calls" % TAG)
    if os.path.lexists(out):
        refuse("%s exists: the outcome of record is write-once" % out)
    check_its_blob()
    heavy_check()
    h0, c0 = emb_table_hashes(emb), corpus_table_sha(db)
    print("%s embeddings_cache per-table hashes BEFORE: %s; corpus_questions %s" % (TAG, h0, c0))
    raw_files = sorted(glob.glob(RAW_GLOB))[:RAW_N] if raw_files is None else raw_files
    kept, L0, smeta = assemble(db, emb, side_path, raw_files, expect_items, side_sha)
    vecs = load_vectors(emb, [v["text"] for v in kept.values()])
    C = corpus_of(kept)
    R = readout(C, vecs)
    h1, c1 = emb_table_hashes(emb), corpus_table_sha(db)
    print("%s embeddings_cache per-table hashes AFTER: %s; corpus_questions %s" % (TAG, h1, c1))
    if h1 != h0 or c1 != c0:
        refuse("a DB of record changed during the readout (embeddings %s -> %s; corpus_questions %s -> %s): nothing written"
               % (h0, h1, c0, c1))
    VL, g1 = verdict_lines(R)
    L = header(smeta) + ["hashes before and after, unchanged: embeddings_cache %s; corpus_questions %s" % (h0, c0)] + L0
    L += support_lines(len(kept), R["r"]["null_sd"]) + [R["audit"]] + VL + [DOES_NOT_SHOW]
    for ln in L:
        print(ln)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("%s wrote %s (write-once, of record)" % (TAG, out))
    return R, g1


# ------------------------------------------------------------------------------------------------ selftest fixture
def _fx_layout():
    """91 src in 14 categories (7 x 7 + 7 x 6), src k's category by that layout."""
    cats, srcs = [], []
    for c in range(K_C):
        for j in range(7 if c < 7 else 6):
            cats.append("cat%02d" % c)
            srcs.append("src-%02d-%d" % (c, j))
    return srcs, cats


def build_fixture(td, geometric=True, per=11):
    """Writes corpus DB, embeddings DB, side export, raw files under td. -> (paths, expected). The layout and every planted
    exclusion are listed in `exp` so the selftest asserts exact values (not that a line exists)."""
    rng = np.random.default_rng(7 if geometric else 8)
    srcs, cats = _fx_layout()
    ccent = ITS.unit(rng.normal(size=(K_C, SLICE)))
    gcent = ITS.unit(rng.normal(size=(K_C, SLICE)))          # anti-aligned clusters for the non-geometric fixture
    scent, ocent = {}, {}           # dims 0-255: the planted structure; dims 256-511 (3x stronger): the OTHER one, so slice 512
    for k, s in enumerate(srcs):     # reads the opposite verdict (a slice-512 mutant flips both fixtures)
        al = ITS.unit((ccent[int(cats[k][3:])] + 0.15 * ITS.unit(rng.normal(size=(1, SLICE)))[0])[None])[0]
        an = ITS.unit((gcent[k % K_C] + 0.15 * ITS.unit(rng.normal(size=(1, SLICE)))[0])[None])[0]
        scent[s], ocent[s] = (al, an) if geometric else (an, al)
    docs, rows, side, vec = [], [], {}, {}
    qid = [1000]

    def doc(s, cat, opts, text):
        qid[0] += 1
        docs.append({"question_id": qid[0], "src": s, "category": cat, "options": opts, "question": text})
        return qid[0]

    def row(text, dom, opts, up, sd, corpora=CORPUS_TAG, v=None, w=None):
        qn = len(rows) + 1
        rows.append((qn, "MMLU_PRO", up, "t", dom, text, json.dumps(opts), "A", "mc", 0))
        it = "i:" + SS.stem_key(text)
        side[it] = (sd, dom, corpora)
        if v is not None:
            vec[text] = np.concatenate([v, w if w is not None else 0.001 * rng.normal(size=SLICE)])
        return it

    def noisy(c):
        return ITS.unit((c + 0.05 * rng.normal(size=SLICE))[None])[0]
    truth, ttext = {}, {}
    for k, s in enumerate(srcs):
        for j in range(per):
            text = "Question %s number %d?" % (s, j)
            opts = [" opt %s %d a " % (s, j), "opt %s %d b" % (s, j)]
            q = doc(s, cats[k], opts, text)
            it = row(text, cats[k], opts, q, "TRAIN", v=noisy(scent[s]), w=3.0 * noisy(ocent[s]))
            truth[it], ttext[it] = (s, cats[k]), text
    exp = {"unmatched": 0, "ambiguous": 0, "multi_src": 0, "eval_no_src": 0, "eval_items": 0, "upstream_disagree": 0}
    # (1) an unmatched TRAIN row (its options are in no raw doc): excluded, no src
    row("Orphan question with no source?", cats[0], ["zz1", "zz2"], 1, "TRAIN", v=noisy(ccent[5]))
    exp["unmatched"] += 1
    # (2) an ambiguous key: two docs of different src share one options list
    amb = ["shared a", "shared b"]
    doc(srcs[0], cats[0], amb, "amb doc one")
    doc(srcs[20], cats[20], amb, "amb doc two")
    row("Ambiguous question?", cats[0], amb, 2, "TRAIN", v=noisy(ccent[6]))
    exp["ambiguous"] += 1
    # (3) a multi-src item: two rows of one stem (case / spacing differ), options of two different src
    o1, o2 = ["ms one a", "ms one b"], ["ms two a", "ms two b"]
    q1 = doc(srcs[1], cats[1], o1, "ms1")
    q2 = doc(srcs[30], cats[30], o2, "ms2")
    row("Multi source question?", cats[1], o1, q1, "TRAIN", v=noisy(ccent[7]))
    row("multi   SOURCE question?", cats[30], o2, q2, "TRAIN", v=noisy(ccent[8]))
    exp["multi_src"] += 1
    # (4) the text-join trap: the row's TEXT is doc X's question, its OPTIONS are doc Y's (another src): options decide -> Y
    ox = ["trap x a", "trap x b"]
    oy = ["trap y a", "trap y b"]
    qx = doc(srcs[2], cats[2], ox, "Trap question text?")
    doc(srcs[50], cats[50], oy, "something else entirely")
    it = row("Trap question text?", cats[50], oy, qx, "TRAIN", v=noisy(scent[srcs[50]]))
    truth[it], ttext[it] = (srcs[50], cats[50]), "Trap question text?"
    exp["upstream_disagree"] += 1
    # (5) a two-row item of one src: the smaller question_id text represents it (its vector is the right one)
    o5 = ["rep a", "rep b"]
    q5 = doc(srcs[3], cats[3], o5, "Representative question?")
    it5 = row("Representative question?", cats[3], o5, q5, "TRAIN", v=noisy(scent[srcs[3]]))
    row("representative  QUESTION?", cats[3], o5, q5, "TRAIN", v=noisy(-scent[srcs[3]]))
    truth[it5], ttext[it5] = (srcs[3], cats[3]), "Representative question?"      # the smaller question_id's text
    # (6) EVAL items (planted on the WRONG categories: if EVAL entered the fit, the counts refuse and H moves), 2 without src
    for j in range(12):
        s = srcs[(j * 7) % len(srcs)]
        text = "Eval question %d?" % j
        opts = ["ev %d a" % j, "ev %d b" % j]
        if j < 10:
            q = doc(s, cats[(j * 7) % len(srcs)], opts, text)
        else:
            q, opts = 0, ["no src %d" % j, "x"]
        row(text, cats[(j * 7) % len(srcs)], opts, q, "EVAL", v=noisy(ccent[(j + 3) % K_C]))
        exp["eval_items"] += 1
        exp["eval_no_src"] += int(j >= 10)
    # (7) GATE rows and a row not tagged mc6, a blank row, a foreign source row
    for j in range(3):
        text = "Gate question %d?" % j
        opts = ["gt %d a" % j, "gt %d b" % j]
        q = doc(srcs[j], cats[j], opts, text)
        row(text, cats[j], opts, q, "GATE", v=noisy(ccent[(j + 9) % K_C]))
    text = "Untagged question?"
    opts = ["un a", "un b"]
    q = doc(srcs[4], cats[4], opts, text)
    row(text, cats[4], opts, q, "TRAIN", corpora="mmlu-pro-v2", v=noisy(ccent[10]))
    rows.append((len(rows) + 1, "MMLU_PRO", 9, "t", cats[0], "   ", json.dumps(["b"]), "A", "mc", 0))
    rows.append((len(rows) + 1, "BBH", 9, "t", "x", "A BBH question?", None, "A", "mc", 0))
    exp["train_items"] = len([1 for it, (sd, _d, c) in side.items() if sd == "TRAIN" and c == CORPUS_TAG])
    exp["kept"] = len(truth)
    exp["truth"] = truth
    # files
    db = os.path.join(td, "mc.db")
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE corpus_questions (question_id INTEGER PRIMARY KEY, source TEXT NOT NULL, upstream_id INTEGER NOT NULL, "
                "task TEXT NOT NULL, domain TEXT NOT NULL, text TEXT NOT NULL, options_json TEXT, target TEXT, verifier TEXT NOT "
                "NULL, generative INTEGER NOT NULL)")
    con.executemany("INSERT INTO corpus_questions VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    con.commit()
    con.close()
    emb = os.path.join(td, "emb.db")
    con = sqlite3.connect(emb)
    con.execute("CREATE TABLE embeddings (query TEXT PRIMARY KEY, vector BLOB)")
    con.execute("CREATE TABLE queries (id INTEGER PRIMARY KEY, query_text TEXT)")
    pad = rng.normal(size=(len(vec), NATIVE_DIM - SLICE2)) * 0.001
    con.executemany("INSERT INTO embeddings VALUES (?, ?)", [(t, np.concatenate([v, pad[i]]).astype(">f4").tobytes())
                                                              for i, (t, v) in enumerate(sorted(vec.items()))])
    con.execute("INSERT INTO queries VALUES (1, 'q')")
    con.commit()
    con.close()
    from data_v2 import split as DS
    trows = sorted((it, "c:" + it[2:], sd, "MMLU_PRO", dom, corp) for it, (sd, dom, corp) in side.items())
    sp = os.path.join(td, "side.tsv")
    with open(sp, "w", encoding="utf-8", newline="\n") as f:
        f.write("# %s table_sha=%s rows=%d split_sha256=%s\n" % (DS.SIDE_EXPORT_FORMAT, DS._side_rows_sha(trows), len(trows), "0" * 64))
        f.write("\t".join(DS.SIDE_COLS) + "\n")
        for r in trows:
            f.write("\t".join(r) + "\n")
    with open(sp, "rb") as f:
        side_sha = hashlib.sha256(f.read()).hexdigest()
    raws = []
    for m in range(RAW_N):
        p = os.path.join(td, "raw", "m%d" % m, "org", "samples_leaderboard_mmlu_pro_2025.jsonl")
        os.makedirs(os.path.dirname(p))
        with open(p, "w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps({"doc": d, "resps": ["..."]}) + "\n")
        raws.append(p)
    exp["digest"] = _digest_of(truth)
    exp["text_digest"] = text_digest({it: {"text": t} for it, t in ttext.items()})
    return {"db": db, "emb": emb, "side": sp, "side_sha": side_sha, "raw": raws}, exp


def _digest_of(truth):
    h = hashlib.sha256()
    for it in sorted(truth):
        h.update(("%s\t%s\t%s\n" % (it, truth[it][0], truth[it][1])).encode("utf-8"))
    return h.hexdigest()[:16]


def _cap(fn):
    buf, err, res = io.StringIO(), None, None
    with contextlib.redirect_stdout(buf):
        try:
            res = fn()
        except SystemExit as ex:
            err = str(ex)
    return buf.getvalue(), err, res


def _line(out, prefix):
    lines = [ln[len(TAG) + 1:] if ln.startswith(TAG + " ") else ln for ln in out.splitlines()]
    got = [ln for ln in lines if ln.startswith(prefix)]
    return got[0] if got else ""


def selftest(only=None, quiet=False, fixture=None):
    n = [0]
    sel = (lambda k: only is None or k in only)

    def ok(c, what):
        n[0] += 1
        if not bool(c):
            raise AssertionError("SELFTEST FAILED: " + what)
        if not quiet:
            print("  ok  " + what)
    g = globals()
    saved = g["_foreign_heavy"]
    g["_foreign_heavy"] = lambda: []
    try:
        if fixture is None:
            with tempfile.TemporaryDirectory() as td:
                _selftest(sel, ok, td, make_fixtures(td))
        else:
            _selftest(sel, ok, fixture[0], fixture[1])
    finally:
        g["_foreign_heavy"] = saved
    if not quiet:
        print("SELFTEST: %d checks passed" % n[0])
    return 0


def _run(fx, td, tag, **kw):
    (p, exp) = fx
    out = os.path.join(td, "out_%s_%d" % (tag, len(os.listdir(td))), "outcome.txt")
    args = dict(db=p["db"], emb=p["emb"], side_path=p["side"], raw_files=p["raw"], out=out, expect_items=exp["train_items"],
                side_sha=p["side_sha"])
    args.update(kw)
    o, err, res = _cap(lambda: main_run(**args))
    return o, err, res, out


def _selftest(sel, ok, td, fx):
    g = globals()
    if sel("ST-CONST"):
        ok((K_C, K_F, MIN_ITEMS, MIN_FINE_PER_CAT, EXPECT_TRAIN_ITEMS, SLICE, SLICE2, D2_REPS, BOOT_B) ==
           (14, 91, 10, 2, 6992, 256, 512, 1000, 1000), "ST-CONST registered constants (K_c 14, K_f 91, >= 10 items, >= 2 per "
           "category, census 6,992, slice 256 decides / 512 printed, 1,000 permutations, B 1,000)")
        ok(PRED_H == (0.30, 0.12, 0.50) and PRED_P == 0.85 and H_BESIDE == (("CLINC qwen3", 0.1429), ("MASSIVE qwen3", 0.4040)),
           "ST-CONST prediction H 0.30 [0.12, 0.50], p 0.85; beside CLINC 0.1429 / MASSIVE 0.4040")
        ok(check_its_blob() == ITS_BLOB, "ST-CONST intent_transfer_s0.py is the registered blob f662ceb (imported unchanged)")
        ok(okey([" a ", "b"]) == '["a", "b"]' and okey(["\u00e9"]) == '["\u00e9"]', "ST-CONST options key = json.dumps of the "
           "stripped options, ensure_ascii False")
    if sel("ST-VERDICT"):
        ok(g1_verdict(0.30, 0.03) == "HELD" and g1_verdict(0.03, 0.03) == "FAILED" and g1_verdict(0.02, 0.03) == "FAILED"
           and g1_verdict(np.float64(0.0300001), np.float64(0.03)) == "HELD", "ST-VERDICT G-1 HELD iff H > p95 (H == p95 FAILED; "
           "numpy scalars)")
        ok(in_interval(0.12, 0.12, 0.50) == "HELD" and in_interval(0.50, 0.12, 0.50) == "HELD" and
           in_interval(0.1199, 0.12, 0.50) == "FAILED" and in_interval(0.5001, 0.12, 0.50) == "FAILED",
           "ST-VERDICT prediction interval closed at both ends")
        ok(abs(brier(0.85, True) - 0.0225) < 1e-12 and abs(brier(0.85, False) - 0.7225) < 1e-12, "ST-VERDICT Brier 0.0225 / 0.7225")
        def RR(H, p95, lo, h512, p512):
            return {"r": {"H": H, "p95": p95, "null_mean": 0.0, "null_sd": 0.02, "n_fine": 91, "k_c": 14, "clusters": 14},
                    "r512": {"H": h512, "p95": p512}, "bs": {"lo": lo, "hi": 0.9, "se": 0.1, "B": 1000}}
        VL, g1 = verdict_lines(RR(0.0500, 0.0400, 0.0100, 0.0100, 0.0400))
        ok(g1 == "HELD" and "G-1: HELD (H 0.0500 > p95 0.0400; the point decides)" in VL and "F-G1: NOT FIRED" in VL,
           "ST-VERDICT verdict_lines: the 256 POINT decides HELD while the bootstrap lower limit and slice 512 sit below p95")
        VL, g1 = verdict_lines(RR(0.0400, 0.0400, 0.0390, 0.9000, 0.0400))
        ok(g1 == "FAILED" and "G-1: FAILED (H 0.0400 <= p95 0.0400; the point decides)" in VL and
           any(x.startswith("F-G1: FIRED") for x in VL) and "PREDICTION G-1 HELD p 0.85: event FAILED, Brier 0.7225" in VL,
           "ST-VERDICT verdict_lines: H == p95 reads FAILED, F-G1 FIRED, Brier 0.7225 (slice 512 above its p95 does not decide)")
        groups = [np.arange(0, 3), np.arange(3, 13), np.arange(13, 14)]
        rr = np.random.default_rng(1)
        lab = np.repeat([0, 1, 2], [3, 10, 1])
        dr = [resample_within(groups, rr) for _ in range(200)]
        ok(all(np.array_equal(np.bincount(lab[d], minlength=3), [3, 10, 1]) for d in dr) and any(len(set(d.tolist())) < 14 for d in dr),
           "ST-VERDICT the item bootstrap resamples WITHIN fine labels (every draw keeps the per-label counts 3 / 10 / 1)")
        Cb = ITS.Corpus("bs", [{"item_id": "i:%02d" % i, "text": "t%d" % i, "coarse": "c%d" % (i % 2), "fine": "f%d" % (i % 4),
                                "side": SS.TRAIN, "hash_side": SS.TRAIN, "is_oos": 0, "drop_reason": None, "stem_key": "%d" % i,
                                "annot": None} for i in range(16)])
        seen = []
        real_hp = g["h_point"]
        g["h_point"] = lambda X, fine, coarse, kc=K_C: seen.append(sorted(np.unique(fine, return_counts=True)[1].tolist())) or 0.5
        try:
            Sb = ITS.Space({"t%d" % i: np.eye(SLICE2)[i % 4] + 0.0 for i in range(16)}, Cb, SLICE)
            bsr = item_bootstrap(Cb, Sb, B=50, seed=3)
        finally:
            g["h_point"] = real_hp
        ok(len(seen) == 50 and all(x == [4, 4, 4, 4] for x in seen) and bsr["lo"] == 0.5 and bsr["B"] == 50,
           "ST-VERDICT item_bootstrap: 50 draws, each with 4 labels x 4 items (within-label), CI from the draws")
        with s0_slot():
            ok(II.GOLD_K[NAME] == (14, 91) and ITS.CORPORA.index(NAME) == 3, "ST-VERDICT GB1 slot: K (14, 91), index 3 -> seed 2105")
        ok(NAME not in II.GOLD_K and ITS.CORPORA == II.CORPORA, "ST-VERDICT GB1 slot restored after the call")
    if sel("ST-E2E"):
        o, err, res, out = _run(fx["geo"], td, "geo")
        exp = fx["geo"][1]
        ok(err is None and res is not None, "ST-E2E geometric fixture: --run completes (%s)" % err)
        R, g1 = res
        ok(g1 == "HELD" and _line(o, "G-1:").startswith("G-1: HELD (H 1.0000 >"), "ST-E2E geometric: G-1 HELD with H 1.0000 "
           "printed: %r" % _line(o, "G-1:"))
        ok(_line(o, "F-G1:") == "F-G1: NOT FIRED", "ST-E2E geometric: F-G1 NOT FIRED")
        ok(_line(o, "PREDICTION H") == "PREDICTION H 0.30 [0.12, 0.50] (80%): FAILED (H 1.0000)", "ST-E2E geometric: prediction "
           "H FAILED (1.0 outside [0.12, 0.50])")
        ok(_line(o, "PREDICTION G-1") == "PREDICTION G-1 HELD p 0.85: event HELD, Brier 0.0225", "ST-E2E geometric: Brier 0.0225")
        ok(R["r"]["n_fine"] == 91 and R["r"]["k_c"] == 14 and R["r"]["clusters"] == 14, "ST-E2E 91 labels cut into 14 clusters")
        # independent recomputation of the null p95 at seed 2105 over the fixture's gold map
        srcs, cats = _fx_layout()
        gold = ITS.codes([cats[k] for k in np.argsort(srcs)])
        rng = np.random.default_rng(2105)
        p95 = float(np.percentile([ITS.ari(gold, rng.permutation(gold)) for _ in range(1000)], 95))
        ok(abs(R["r"]["p95"] - p95) < 1e-15, "ST-E2E p95 %.6f == an independent 1,000-permutation p95 at seed 2105 (%.6f)"
           % (R["r"]["p95"], p95))
        ok("p95 = %.4f" % p95 in _line(o, "READOUT H"), "ST-E2E the printed p95 is that value")
        ok(_line(o, "options-key join").startswith("options-key join (never text) on TRAIN rows: matched %d, unmatched 1, "
                                                  "ambiguous 1" % (91 * 11 + 1 + 2 + 2)),
           "ST-E2E join counts: matched %d / unmatched 1 / ambiguous 1: %r" % (91 * 11 + 5, _line(o, "options-key join")))
        ok("upstream_id == matched doc question_id on %d of %d" % (91 * 11 + 4, 91 * 11 + 5) in _line(o, "options-key join"),
           "ST-E2E upstream agreement printed (the trap row disagrees)")
        ok(("assignment digest %s" % exp["digest"]) in _line(o, "TRAIN items excluded"), "ST-E2E item -> (src, category) "
           "assignment digest equals the fixture's truth (options decide; the text-join trap goes to src Y)")
        ok(("text digest %s)" % exp["text_digest"]) in _line(o, "TRAIN items excluded"), "ST-E2E each item's text is its "
           "smallest-question_id row's (text digest equals the fixture's truth)")
        ok(_line(o, "TRAIN items excluded").startswith("TRAIN items excluded: no src 2, multi-src 1, multi-domain 0; kept %d"
                                                       % exp["kept"]), "ST-E2E exclusions: no src 2 (unmatched + ambiguous), "
           "multi-src 1: %r" % _line(o, "TRAIN items excluded"))
        ok(_line(o, "EVAL items without src") == "EVAL items without src: 2 of 12 (disclosed and excluded; a count only, no EVAL "
           "vector or label is read; R-2)", "ST-E2E EVAL items without src: 2 of 12")
        ok("TRAIN rows %d -> %d texts -> %d items" % (91 * 11 + 7, 91 * 11 + 7, exp["train_items"]) in _line(o, "member MMLU_PRO_LB"),
           "ST-E2E member census rows -> texts -> items: %r" % _line(o, "member MMLU_PRO_LB"))
        ok("EVAL rows 12 / items 12; GATE rows 3; blank 1; no side 0; not tagged 1" in _line(o, "member MMLU_PRO_LB"),
           "ST-E2E EVAL / GATE / blank / untagged counted, never in the fit")
        ok(_line(o, "TRAIN-ONLY:").startswith("TRAIN-ONLY:") and "0 with an EVAL row" in o, "ST-E2E TRAIN-ONLY audit: 0 EVAL rows")
        lo, hi = R["bs"]["lo"], R["bs"]["hi"]
        ok(lo == 1.0 and hi == 1.0 and "95% [1.0000, 1.0000]" in _line(o, "READOUT item bootstrap"), "ST-E2E item bootstrap CI "
           "[1, 1] on well-separated labels")
        ok(R["r512"]["H"] <= R["r512"]["p95"] and _line(o, "READOUT slice 512") == "READOUT slice 512 (printed, never deciding): "
           "H %.4f, p95 %.4f" % (R["r512"]["H"], R["r512"]["p95"]), "ST-E2E slice 512 printed (the planted opposite structure: H "
           "%.4f <= its p95), never deciding" % R["r512"]["H"])
        ok("MEASURED: null SD %.4f" % R["r"]["null_sd"] in o and R["r"]["null_sd"] > 0, "ST-E2E measured null SD printed")
        with open(out, encoding="utf-8") as f:
            body = f.read()
        ok("G-1: HELD" in body and "F-G1: NOT FIRED" in body and DOES_NOT_SHOW in body, "ST-E2E the outcome file carries the "
           "verdict, the falsifier and DOES NOT SHOW")
        o2, err2, _r, _o = _run(fx["geo"], td, "geo", out=out)
        with open(out, encoding="utf-8") as f:
            ok(err2 is not None and "write-once" in err2 and f.read() == body, "ST-E2E second --run on the same path REFUSES; the "
               "file is unchanged")
        # non-geometric fixture
        o, err, res, out = _run(fx["non"], td, "non")
        ok(err is None and res[1] == "FAILED", "ST-E2E anti-aligned fixture: G-1 FAILED (%s)" % err)
        H = res[0]["r"]["H"]
        ok(H <= res[0]["r"]["p95"] and _line(o, "G-1:") == "G-1: FAILED (H %.4f <= p95 %.4f; the point decides)" % (H, res[0]["r"]["p95"]),
           "ST-E2E anti-aligned: the G-1 line prints FAILED with '<=': %r" % _line(o, "G-1:"))
        ok(_line(o, "F-G1:").startswith("F-G1: FIRED (the declared categories are not a geometric level"), "ST-E2E anti-aligned: "
           "F-G1 FIRED printed")
        ok(_line(o, "PREDICTION G-1") == "PREDICTION G-1 HELD p 0.85: event FAILED, Brier 0.7225", "ST-E2E anti-aligned: Brier 0.7225")
        ok(_line(o, "PREDICTION H") == "PREDICTION H 0.30 [0.12, 0.50] (80%%): FAILED (H %.4f)" % H, "ST-E2E anti-aligned: "
           "prediction H scored FAILED")
    if sel("ST-REFUSE"):
        p, exp = fx["geo"]

        def refused(why, **kw):
            o, err, res, out = _run(fx["geo"], td, "ref", **kw)
            return err is not None and why in err and not os.path.exists(out)
        ok(refused("TRAIN items", expect_items=exp["train_items"] + 1), "ST-REFUSE item count != the census bracket REFUSES")
        ok(refused("LF sha256", side_sha="0" * 64), "ST-REFUSE side export pin mismatch REFUSES")
        g["_foreign_heavy"] = lambda: ['"java.exe","123"']
        try:
            ok(refused("foreign heavy"), "ST-REFUSE a running java.exe REFUSES the --run")
            o, err, _r = _cap(lambda: dry_run(p["db"], p["emb"], p["side"], p["raw"], exp["train_items"], p["side_sha"]))
            ok(err is not None and "foreign heavy" in err, "ST-REFUSE a running java.exe REFUSES the --dry-run")
        finally:
            g["_foreign_heavy"] = lambda: []
        # raw files disagree
        bad = os.path.join(td, "rawbad.jsonl")
        with open(p["raw"][0], encoding="utf-8") as f, open(bad, "w", encoding="utf-8") as h:
            for i, ln in enumerate(f):
                d = json.loads(ln)
                if i == 5:
                    d["doc"]["src"] = "src-other"
                h.write(json.dumps(d) + "\n")
        ok(refused("disagree", raw_files=p["raw"][:2] + [bad]), "ST-REFUSE raw files disagreeing on a src REFUSES")
        # a DB of record changing during the readout
        real = g["emb_table_hashes"]
        calls = [0]

        def drift(path):
            calls[0] += 1
            h = real(path)
            if calls[0] > 1:
                h = dict(h, embeddings="changed")
            return h
        g["emb_table_hashes"] = drift
        try:
            ok(refused("changed during the readout"), "ST-REFUSE embeddings table hash changed before -> after REFUSES, nothing written")
        finally:
            g["emb_table_hashes"] = real
        # label-structure refusals on modified kept sets
        kept = {"i:%03d" % i: {"src": "s%d" % (i % 91), "dom": "c%d" % ((i % 91) % 14), "text": "t", "comp": ""} for i in range(91 * 10)}
        o, err, lab = _cap(lambda: label_census(kept))
        ok(err is None and lab["n_fine"] == 91 and lab["min"] == 10, "ST-REFUSE label census passes at 91 x 10")
        k2 = dict(kept)
        k2["i:x"] = {"src": "s0", "dom": "c5", "text": "t", "comp": ""}
        ok("nesting" in (_cap(lambda: label_census(k2))[1] or ""), "ST-REFUSE a src under two categories REFUSES (nesting)")
        k3 = {k: v for k, v in kept.items() if not (v["src"] == "s7" and int(k[2:]) >= 91 * 9)}
        ok("< 10 TRAIN items" in (_cap(lambda: label_census(k3))[1] or ""), "ST-REFUSE a label with 9 TRAIN items REFUSES")
        k4 = {k: v for k, v in kept.items() if v["src"] != "s90"}
        ok("90 fine labels" in (_cap(lambda: label_census(k4))[1] or ""), "ST-REFUSE 90 fine labels REFUSES")
        k5 = {k: (dict(v, dom="c0") if v["dom"] == "c13" and v["src"] != "s13" else v) for k, v in kept.items()}
        ok("< 2 fine labels" in (_cap(lambda: label_census(k5))[1] or ""), "ST-REFUSE a category with 1 fine label REFUSES (declined)")
        # a missing vector
        o, err, _r = _cap(lambda: load_vectors(p["emb"], ["Question src-00-0 number 0?", "no such text"]))
        ok(err is not None and "1 item texts have no vector" in err, "ST-REFUSE a missing vector REFUSES")
        # dry run: nothing written, no H
        o, err, _r = _cap(lambda: dry_run(p["db"], p["emb"], p["side"], p["raw"], exp["train_items"], p["side_sha"]))
        ok(err is None and "DRY RUN complete: %d TRAIN items, 91 fine labels; nothing written" % exp["kept"] in o and "G-1" not in o
           and "READOUT" not in o, "ST-REFUSE --dry-run assembles the member and computes no H")
        # the replica guard: a d2 result that disagrees with the replica REFUSES
        real_d2 = ITS.d2
        ITS.d2 = lambda C, S: dict(real_d2(C, S), p95=-1.0)
        try:
            ok(refused("replica disagrees"), "ST-REFUSE the d2 / replica disagreement guard REFUSES")
        finally:
            ITS.d2 = real_d2


MUTANTS = (
    ("G-1 at H >= p95", "    return \"HELD\" if bool(float(H) > float(p95)) else \"FAILED\"", "    return \"HELD\" if bool(float(H) >= float(p95)) else \"FAILED\"", ("ST-VERDICT",)),
    ("G-1 decided on the bootstrap lower limit", "    g1 = g1_verdict(r[\"H\"], r[\"p95\"])\n", "    g1 = g1_verdict(bs[\"lo\"], r[\"p95\"])\n", ("ST-VERDICT",)),
    ("G-1 decided on the slice-512 readout", "    g1 = g1_verdict(r[\"H\"], r[\"p95\"])\n", "    g1 = g1_verdict(r512[\"H\"], r512[\"p95\"])\n", ("ST-VERDICT", "ST-E2E")),
    ("slice 512 decides in the readout", "    r, S = geometry(C, vecs, SLICE)\n", "    r, S = geometry(C, vecs, SLICE2)\n", ("ST-E2E",)),
    ("replica p95 -> p5", "    return {\"p95\": float(np.percentile(null, 95)),", "    return {\"p95\": float(np.percentile(null, 5)),", ("ST-E2E",)),
    ("replica guard removed", "    if hp != r[\"H\"] or rep[\"p95\"] != r[\"p95\"]:\n", "    if False:\n", ("ST-REFUSE",)),
    ("join by text", "        hits = byk.get(okey(DC.extract_options(opts)), set())\n", "        hits = TEXT_INDEX.get(text, set())\n", ("ST-E2E",)),
    ("options not stripped", "    return json.dumps([o.strip() for o in opts], ensure_ascii=False)", "    return json.dumps(list(opts), ensure_ascii=False)", ("ST-CONST", "ST-E2E")),
    ("ambiguous key kept (first src)", "        elif len(srcs) > 1:\n            cnt[\"train_ambiguous\"] += 1\n", "        elif False:\n            cnt[\"train_ambiguous\"] += 1\n", ("ST-E2E",)),
    ("multi-src item kept", "        if len(e[\"src\"]) > 1:\n            ex[\"multi_src\"] += 1\n            continue\n", "", ("ST-E2E",)),
    ("EVAL rows enter TRAIN", "        if side == \"EVAL\":\n", "        if side == \"EVAL-NEVER\":\n", ("ST-E2E",)),
    ("GATE rows enter TRAIN", "        if side != \"TRAIN\":\n", "        if side not in (\"TRAIN\", \"GATE\"):\n", ("ST-E2E",)),
    ("untagged rows kept", "        if CORPUS_TAG not in corpora:\n", "        if False:\n", ("ST-E2E",)),
    ("EVAL-without-src counted from TRAIN", "    cnt[\"eval_no_src\"] = sum(1 for v in ev.values() if not v)\n", "    cnt[\"eval_no_src\"] = cnt[\"train_unmatched\"]\n", ("ST-E2E",)),
    ("representative = largest question_id", "        qid, text = min(e[\"rows\"])\n", "        qid, text = max(e[\"rows\"])\n", ("ST-E2E",)),
    ("nesting check removed", "    if bad:\n        refuse(\"nesting", "    if False:\n        refuse(\"nesting", ("ST-REFUSE",)),
    ("label minimum 10 -> 9", "MIN_ITEMS, MIN_FINE_PER_CAT = 10, 2\n", "MIN_ITEMS, MIN_FINE_PER_CAT = 9, 2\n", ("ST-CONST",)),
    ("label minimum check removed", "    if small:\n", "    if False:\n", ("ST-REFUSE",)),
    ("K_f check removed", "    if len(n_src) != K_F:\n", "    if False:\n", ("ST-REFUSE",)),
    ("category >= 2 check removed", "    if thin:\n", "    if False:\n", ("ST-REFUSE",)),
    ("K_c 13", "K_C, K_F = 14, 91\n", "K_C, K_F = 13, 91\n", ("ST-CONST",)),
    ("census check removed", "    if cnt[\"train_items\"] != expect_items:\n", "    if False:\n", ("ST-REFUSE",)),
    ("side pin unchecked", "    if smeta[\"sha256_lf\"] != side_sha:\n", "    if False:\n", ("ST-REFUSE",)),
    ("raw agreement unchecked", "    if any(p != per[0] for p in per[1:]):\n", "    if False:\n", ("ST-REFUSE",)),
    ("heavy check skipped", "    if heavy:\n        refuse(", "    if False:\n        refuse(", ("ST-REFUSE",)),
    ("heavy check not in the dry run", "    check_its_blob()\n    heavy_check()\n    raw_files = sorted(glob.glob(RAW_GLOB))[:RAW_N] if raw_files is None else raw_files\n    kept, L, smeta",
     "    check_its_blob()\n    raw_files = sorted(glob.glob(RAW_GLOB))[:RAW_N] if raw_files is None else raw_files\n    kept, L, smeta", ("ST-REFUSE",)),
    ("table hash after-check skipped", "    if h1 != h0 or c1 != c0:\n", "    if False:\n", ("ST-REFUSE",)),
    ("missing vector tolerated", "    if len(out) != len(want):\n", "    if False:\n", ("ST-REFUSE",)),
    ("outcome not write-once (no exists check, mode w)", [("    if os.path.lexists(out):\n        refuse(", "    if False:\n        refuse("),
                                                          ("    with open(out, \"x\", encoding", "    with open(out, \"w\", encoding")], None, ("ST-E2E",)),
    ("F-G1 fires on HELD", "    if held:\n        L.append(\"F-G1: NOT FIRED\")\n", "    if not held:\n        L.append(\"F-G1: NOT FIRED\")\n", ("ST-E2E",)),
    ("F-G1 FIRED line never printed", "        L.append(\"F-G1: FIRED (the declared", "        (\"F-G1: FIRED (the declared", ("ST-E2E",)),
    ("Brier on the wrong event", "brier(PRED_P, held)", "brier(PRED_P, not held)", ("ST-E2E",)),
    ("prediction interval open", "    return \"HELD\" if bool(lo <= float(v) <= hi) else \"FAILED\"", "    return \"HELD\" if bool(lo < float(v) < hi) else \"FAILED\"", ("ST-VERDICT",)),
    ("bootstrap across labels (not within)", "    return np.concatenate([g[rng.integers(len(g), size=len(g))] for g in groups])\n",
     "    allg = np.concatenate(groups)\n    return allg[rng.integers(len(allg), size=len(allg))]\n", ("ST-VERDICT",)),
    ("bootstrap bypasses the within-label draw", "        idx = resample_within(groups, rng)\n",
     "        idx = np.concatenate(groups)[rng.integers(sum(len(x) for x in groups), size=sum(len(x) for x in groups))]\n", ("ST-VERDICT",)),
    ("GB1 slot not restored", "        ITS.CORPORA = saved_c\n", "        pass\n", ("ST-VERDICT",)),
    ("dry run computes and writes", "    print(\"%s DRY RUN complete", "    main_run(db, emb, side_path, raw_files, os.path.join(os.path.dirname(db), 'dry_out.txt'), expect_items, side_sha)\n    print(\"%s DRY RUN complete", ("ST-REFUSE",)),
)


def make_fixtures(td):
    for d in ("g", "n"):
        os.makedirs(os.path.join(td, d))
    return {"geo": build_fixture(os.path.join(td, "g"), True), "non": build_fixture(os.path.join(td, "n"), False)}


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    td = tempfile.mkdtemp(prefix="gold_geom_mut_")
    fx = make_fixtures(td)
    killed = 0
    for name, old, new, tests in MUTANTS:
        pairs = old if isinstance(old, list) else [(old, new)]
        code = head
        for o_, n_ in pairs:
            if code.count(o_) != 1:
                raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, code.count(o_)))
            code = code.replace(o_, n_)
        new = "".join(n_ for _o, n_ in pairs)
        ns = {"__name__": "gold_geom_mutant", "__file__": os.path.abspath(__file__)}
        try:
            if "TEXT_INDEX" in new:      # the text-join mutant needs the raw question text: index it the way a text join would
                code = code.replace("    byk = raw_index(raw)\n", "    byk = raw_index(raw)\n    global TEXT_INDEX\n    TEXT_INDEX = {}\n"
                                    "    for f in raw_files[:1]:\n        for ln in open(f, encoding='utf-8'):\n"
                                    "            d = json.loads(ln)['doc']\n            TEXT_INDEX.setdefault(d['question'], set()).add((d['src'], d['category'], int(d['question_id'])))\n")
            exec(compile(code, "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True, fixture=(td, fx))
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:110])
        killed += res.startswith("KILLED")
        print("  %-48s %s" % (name, res))
    import shutil
    shutil.rmtree(td, ignore_errors=True)
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="MMLU-GOLD-GEOMETRY (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--mutants", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--db", default=DB_FILE)
    ap.add_argument("--emb-db", default=EMB_FILE)
    ap.add_argument("--raw-glob", default=RAW_GLOB)
    ap.add_argument("--out", default=OUT_FILE)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.mutants:
        return run_mutants()
    raw = sorted(glob.glob(a.raw_glob))[:RAW_N]
    if a.dry_run:
        return dry_run(a.db, a.emb_db, SIDE_FILE, raw)
    main_run(a.db, a.emb_db, SIDE_FILE, raw, a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
