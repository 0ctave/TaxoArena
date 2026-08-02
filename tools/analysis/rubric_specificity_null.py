#!/usr/bin/env python3
"""
Random-cell null arm for the rubric-specificity pre-registration
(docs/prereg_rubric_specificity.md).

Two modes:

  prepare   Reads the frozen artifact (READ-ONLY) and writes cell definitions for
            N synthetic cells whose sizes are drawn from the frozen leaf size
            distribution and whose members are drawn at random from the whole
            construction corpus. Cells are disjoint, exactly as the leaf
            partition is.

  measure   Reads the rubrics the Kotlin harness induced on those cells and
            computes, for BOTH arms with one identical code path, the five
            measures of the pre-registration.

Everything here opens snapshots.db and embeddings_cache.db read-only.
"""
import argparse
import json
import os
import random
import re
import sqlite3
import sys
from collections import Counter

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FROZEN = "20260727_042523_Headless_Run_Auto_ge"
OUTDIR = os.path.join(ROOT, "build", "rubric_null")

# Standard English function-word stoplist. Only entries of length >= 4 can ever
# bind, because the term filter already drops shorter tokens.
STOP = set("""a about above after again against all also am an and any are aren't as at be because
been before being below between both but by can cannot could couldn't did didn't do does doesn't
doing don't down during each few for from further had hadn't has hasn't have haven't having he her
here hers herself him himself his how i if in into is isn't it its itself just let's me more most
mustn't my myself no nor not of off on once only or other ought our ours ourselves out over own
same shan't she should shouldn't so some such than that the their theirs them themselves then there
these they this those through to too under until up very was wasn't we were weren't what when where
which while who whom why with won't would wouldn't you your yours yourself yourselves""".split())


def terms(text):
    """Content terms: lowercase alphabetic, length >= 4, stopped."""
    return set(w for w in re.findall(r"[a-z]+", (text or "").lower())
               if len(w) >= 4 and w not in STOP)


def java_hash(s):
    """String.hashCode(), so the 20% induction hold-back can be replayed here."""
    h = 0
    for ch in s:
        h = (31 * h + ord(ch)) & 0xFFFFFFFF
    return h - 2 ** 32 if h >= 2 ** 31 else h


_RESERVED = None


def reserved_texts():
    """The held-out split, resolved exactly as ModelEvalStore.getReservedQuestionTexts does
    (through eval_question_link, not through eval_results.question_text)."""
    global _RESERVED
    if _RESERVED is None:
        con = sqlite3.connect(
            f"file:{os.path.join(ROOT, 'mmlu_pro_dataset_cache_v2.db')}?mode=ro", uri=True)
        _RESERVED = set(r[0] for r in con.execute("""
            SELECT DISTINCT m.question
            FROM reserved_pool p
            JOIN active_reserved_pool a ON a.pool_id = p.pool_id AND a.only_row = 1
            JOIN eval_question_link l ON l.question_id = p.question_id
            JOIN mmlu_pro m ON m.id = l.mmlu_pro_row_id"""))
        con.close()
    return _RESERVED


def induction_subset(texts, qmode):
    """Which of a cell's queries count as "the cell's queries" for measure 4.

    all         every query the cell holds. The plain reading of the prereg, and the
                definition whose leaf-arm numbers land closest to the registered ones.
    hash        minus the 20% TaxonomyJudgeService discards (abs(rawText.hashCode()) % 5 == 0).
    induction   also minus the held-out split — 2437 of the 8299 graph queries — i.e. exactly
                the text the model was shown.

    The original analysis script was never committed, so which of these it used cannot be
    recovered; all three are reported and the arms are always compared under the same one.
    """
    if qmode == "all":
        return list(texts)
    out = [t for t in texts if abs(java_hash(t)) % 5 != 0]
    if qmode == "induction":
        res = reserved_texts()
        out = [t for t in out if t not in res]
    return out


def load_frozen():
    snap_db = os.path.join(ROOT, 'snapshots.db')
    if not os.path.exists(snap_db):  # clone fallback
        snap_db = os.path.join(ROOT, 'snapshots_frozen.db')
    con = sqlite3.connect(f"file:{snap_db}?mode=ro", uri=True)
    row = con.execute("SELECT graph FROM snapshots WHERE id = ?", (FROZEN,)).fetchone()
    if row is None:
        sys.exit(f"frozen snapshot {FROZEN} not found")
    graph = json.loads(row[0])
    con.close()
    leaves = [n for n in graph["nodes"] if not n.get("childIds")]
    return leaves


def load_query_texts():
    con = sqlite3.connect(f"file:{os.path.join(ROOT, 'embeddings_cache.db')}?mode=ro", uri=True)
    m = dict(con.execute("SELECT id, raw_text FROM queries"))
    con.close()
    return m


def q(xs):
    xs = list(xs)
    return np.median(xs), np.percentile(xs, 25), np.percentile(xs, 75)


def fmt(xs, p=3):
    m, lo, hi = q(xs)
    return f"{m:.{p}f} [{lo:.{p}f}, {hi:.{p}f}]"


# ---------------------------------------------------------------- prepare ----

def prepare(n_cells, seed):
    leaves = load_frozen()
    qid2txt = load_query_texts()
    leaf_sizes = [len(l["queryIds"]) for l in leaves]

    corpus = sorted({qid for l in leaves for qid in l["queryIds"]})
    missing = [qid for qid in corpus if qid not in qid2txt]
    if missing:
        sys.exit(f"{len(missing)} construction query ids have no text in embeddings_cache.db")

    rng = random.Random(seed)
    sizes = rng.sample(leaf_sizes, n_cells)          # matches the leaf size distribution
    shuffled = corpus[:]
    rng.shuffle(shuffled)

    if sum(sizes) > len(shuffled):
        sys.exit("sampled sizes exceed the construction corpus")

    cells, ptr = [], 0
    for i, size in enumerate(sizes):
        ids = shuffled[ptr:ptr + size]
        ptr += size
        cells.append({
            "id": f"randcell_{i:02d}",
            # Deliberately uninformative: naming a topic would inject the very
            # coherence the null is meant to remove, and naming it "General"
            # would prompt the model to be generic. "Cluster NN" is the label
            # scripts/generate_baselines.py already uses for structureless cells.
            "label": f"Cluster {i + 1:02d}",
            "size": size,
            "queryIds": ids,
            "queries": [qid2txt[qid] for qid in ids],
        })

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "cells.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"frozenSnapshot": FROZEN, "seed": seed, "cells": cells}, f)

    print(f"wrote {path}")
    print(f"n = {len(cells)} cells, sizes = {sorted(sizes)}")
    print(f"total queries {sum(sizes)} of a {len(corpus)}-query construction corpus (disjoint)")
    lm, ll, lh = q(leaf_sizes)
    sm, sl, sh = q(sizes)
    print(f"leaf sizes   median {lm:.0f} IQR [{ll:.0f}, {lh:.0f}] n=87")
    print(f"sampled      median {sm:.0f} IQR [{sl:.0f}, {sh:.0f}] n={len(sizes)}")
    # What the model will actually be shown, after the 20% induction hold-back.
    ind = [len(induction_subset(c["queries"], "induction")) for c in cells]
    print(f"induction corpus per cell: median {np.median(ind):.0f}, "
          f"batches(25) median {np.median([-(-x // 25) for x in ind]):.0f}")


# ---------------------------------------------------------------- measure ----

def arm_stats(name, rubrics, query_sets, n_others, seed, out):
    """rubrics: list[str]; query_sets: list[set[str]] aligned with rubrics."""
    R = [terms(r) for r in rubrics]
    n = len(R)
    lens = [len(r.split()) for r in rubrics]
    distinct = [len(r) for r in R]
    vocab = set().union(*R) if R else set()
    df = Counter()
    for r in R:
        df.update(r)
    uniq = sum(1 for t, k in df.items() if k == 1)
    ge90 = sum(1 for t, k in df.items() if k >= 0.9 * n)

    jac = []
    for i in range(n):
        for j in range(i + 1, n):
            u = len(R[i] | R[j])
            jac.append(len(R[i] & R[j]) / u if u else 0.0)

    own = [len(R[i] & query_sets[i]) / len(R[i]) if R[i] else 0.0 for i in range(n)]
    rng = random.Random(seed)
    spec, others_mean = [], []
    for i in range(n):
        pool = [j for j in range(n) if j != i]
        others = rng.sample(pool, min(n_others, len(pool)))
        m = float(np.mean([len(R[i] & query_sets[j]) / len(R[i]) for j in others]))
        others_mean.append(m)
        spec.append(own[i] - m)

    out[name] = {
        "n": n,
        "rubric_words": fmt(lens, 0),
        "distinct_terms": fmt(distinct, 0),
        "query_vocab": fmt([len(s) for s in query_sets], 0),
        "jaccard": fmt(jac, 4),
        "vocab": len(vocab),
        "unique_terms": uniq,
        "unique_frac": uniq / len(vocab) if vocab else 0.0,
        "ge90": ge90,
        "own": fmt(own, 3),
        "other": fmt(others_mean, 3),
        "spec": fmt(spec, 3),
        "spec_median": float(np.median(spec)),
        "positive": sum(1 for x in spec if x > 0),
        "raw_spec": spec,
        "raw_own": own,
    }
    return out[name]


def measure(n_others, seed, qmode):
    leaves = load_frozen()
    qid2txt = load_query_texts()

    # --- treatment arm: 87 frozen leaves -------------------------------------
    leaf_rubrics = [l["judgeRubric"] or "" for l in leaves]
    leaf_qsets = []
    for l in leaves:
        texts = induction_subset([qid2txt[q] for q in l["queryIds"]], qmode)
        s = set()
        for t in texts:
            s |= terms(t)
        leaf_qsets.append(s)

    print(f"=== Q_i definition: {qmode} ===")
    results = {}
    arm_stats("leaf-87", leaf_rubrics, leaf_qsets, n_others, seed, results)

    # --- null arm: induced random cells --------------------------------------
    rub_path = os.path.join(OUTDIR, "rubrics.json")
    if os.path.exists(rub_path):
        with open(rub_path, encoding="utf-8") as f:
            induced = json.load(f)
        with open(os.path.join(OUTDIR, "cells.json"), encoding="utf-8") as f:
            cells = {c["id"]: c for c in json.load(f)["cells"]}
        ok = [r for r in induced if r.get("rubric")]
        rand_rubrics = [r["rubric"] for r in ok]
        rand_qsets = []
        for r in ok:
            texts = induction_subset(cells[r["id"]]["queries"], qmode)
            s = set()
            for t in texts:
                s |= terms(t)
            rand_qsets.append(s)
        arm_stats("random-cell", rand_rubrics, rand_qsets, n_others, seed, results)
        # Same-n subsample of the leaf arm. Vocabulary size, unique-term count and the
        # ">=90% of rubrics" count all depend on how many rubrics are pooled, so comparing
        # 13 random rubrics against 87 leaf rubrics on those three would compare n, not arms.
        rng = random.Random(seed)
        idx = rng.sample(range(len(leaves)), len(ok))
        arm_stats(f"leaf-{len(ok)} (subsample)",
                  [leaf_rubrics[i] for i in idx], [leaf_qsets[i] for i in idx],
                  n_others, seed, results)
        # One subsample is itself noisy, so the n-dependent measures get a distribution.
        boot = {"vocab": [], "unique_terms": [], "unique_frac": [], "ge90": [],
                "spec_median": [], "positive": []}
        brng = random.Random(seed + 1)
        scratch = {}
        for _ in range(200):
            bidx = brng.sample(range(len(leaves)), len(ok))
            st = arm_stats("_b", [leaf_rubrics[i] for i in bidx],
                           [leaf_qsets[i] for i in bidx], n_others, brng.randint(0, 10 ** 6),
                           scratch)
            for k in boot:
                boot[k].append(st[k])
        results["leaf-%d bootstrap" % len(ok)] = {
            "n": len(ok),
            "rubric_words": "-", "distinct_terms": "-", "query_vocab": "-",
            "jaccard": "-", "own": "-", "other": "-",
            "spec": fmt(boot["spec_median"], 3),
            "spec_median": float(np.median(boot["spec_median"])),
            "vocab": int(np.median(boot["vocab"])),
            "unique_terms": int(np.median(boot["unique_terms"])),
            "unique_frac": float(np.median(boot["unique_frac"])),
            "ge90": int(np.median(boot["ge90"])),
            "positive": int(np.median(boot["positive"])),
        }
        print("leaf-%d bootstrap (200 draws): vocab %s | unique %s | >=90%% %s | "
              "spec-median %s | positive %s"
              % (len(ok), fmt(boot["vocab"], 0), fmt(boot["unique_terms"], 0),
                 fmt(boot["ge90"], 1), fmt(boot["spec_median"], 3),
                 fmt(boot["positive"], 1)))
    else:
        print(f"(no {rub_path} yet — treatment arm only)\n")

    rows = [
        ("rubric length (words)", "rubric_words"),
        ("distinct content terms", "distinct_terms"),
        ("|Q_i| distinct query terms", "query_vocab"),
        ("pairwise Jaccard", "jaccard"),
        ("own-overlap  |R_i n Q_i|/|R_i|", "own"),
        ("other-overlap (mean)", "other"),
        ("SPECIFICITY own - other", "spec"),
    ]
    names = list(results.keys())
    w = max(len(n) for n in names) + 2
    print(f"{'measure':32s}" + "".join(f"{n:>{max(26, w)}s}" for n in names))
    for label, key in rows:
        print(f"{label:32s}" + "".join(f"{results[n][key]:>{max(26, w)}s}" for n in names))
    for label, key, f in [
        ("vocabulary size", "vocab", "{}"),
        ("terms unique to one rubric", "unique_terms", "{}"),
        ("  as % of vocabulary", "unique_frac", "{:.1%}"),
        ("terms in >=90% of rubrics", "ge90", "{}"),
        ("cells with positive specificity", "positive", "{}"),
        ("n", "n", "{}"),
    ]:
        print(f"{label:32s}" + "".join(f"{f.format(results[n][key]):>{max(26, w)}s}" for n in names))

    if "random-cell" in results:
        x = results["random-cell"]["spec_median"]
        band = ("coherence IS the cause" if x <= 0.05 else
                "specificity is NOT about coherence" if x >= 0.10 else
                "PARTIAL")
        print(f"\nrandom-cell median specificity = {x:.3f}  ->  {band}")

    with open(os.path.join(OUTDIR, f"measures_{qmode}.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["prepare", "measure"])
    ap.add_argument("--cells", type=int, default=13)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--others", type=int, default=12)
    ap.add_argument("--qmode", choices=["all", "hash", "induction"], default="all")
    a = ap.parse_args()
    if a.mode == "prepare":
        prepare(a.cells, a.seed)
    else:
        measure(a.others, a.seed, a.qmode)
