"""ARCH-V2-INDUCE-RUBRIC-1, ruling D1 (coordinator 2026-09-24; the registrar inserting): the ZERO-CALL OVERLAP AUDIT.

EXCLUDE from the induction's inputs every TRAIN candidate that shares a run of >= THRESHOLD (8) consecutive tokens with
any ONE EVAL text; the inducer replaces them in sort order. This separate step is the ONLY process that reads EVAL text for
the purpose; the inducer reads only this step's output list (never eval_view before its reply: ruling on finding 3 (i)).

    python tools/analysis/judge_v2/induce_overlap_audit.py --build [--out PATH]     # writes the list (mode "x")
    python tools/analysis/judge_v2/induce_overlap_audit.py --check PATH             # re-verify a written list's own sha

INPUTS (read-only, sha-pinned through the stage-gated openers):
  eval_view_REG.db (sha256_bytes = the manifest of record's) through data_v2.views.open_eval (stage "judge": the accepted
  mislabel of finding 3 (iv); an "audit" stage is queued); gen_view_REG.db (the registered sha) through open_generation
  ("induce").
  TRAIN CANDIDATES = the C4 population: gen_view variants of corpus_version mmlu-pro-v2, contract MC_LETTER, side TRAIN,
  distinct variant_id (7,927 on the view of record).
  [RE-PIN 2026-09-24: on the SPLIT-2 views of record (CK-CLOSE-v2 redraw, 5a3e756) the count is the new gen_view's; the
  list of record is overlap_exclusions_split2.json; the SPLIT-1 list overlap_exclusions.json is kept, superseded]
  EVAL TEXTS = the stem and EACH option (options_sorted_json) of EVERY variant of eval_view (all corpora, sentinels
  included), each text on its own.
TOKENS = judge_v2.induction._tokens (casefold, \\w+ runs), the same tokenizer as the verbatim audit.
RUN = for one TRAIN text (the candidate's stem or one option) against one EVAL text: the longest chain of ALIGNED 8-grams
  (8-gram at TRAIN position i equal to the 8-gram at EVAL position j, i+1 with j+1, ...), in tokens (chain + 7). A
  candidate's run is its maximum over its texts and all EVAL texts; its matched EVAL variant is the one giving it (ties:
  the smallest EVAL variant_id).
OUTPUT (write-once, mode "x"): JSON {registration, rule, threshold, tokenizer, population, gen_view_sha256_bytes,
  eval_view_sha256_bytes, candidates, n_excluded, n_run_ge_50, excluded: [{variant_id, run, eval_variant_id}] sorted by
  variant_id, audit_blob, list_sha256}. list_sha256 = sha256 of the canonical JSON of everything else. NO EVAL TEXT is
  written: only TRAIN variant ids, run lengths and matched EVAL variant ids.
"""
import argparse
import hashlib
import json
import os
import sys

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

from ._base import dv2views, git_blob_lf, refuse, sha256_text, ROOT  # noqa: E402
from . import induction as I  # noqa: E402

REGISTRATION = "ARCH-V2-INDUCE-RUBRIC-1 (ruling D1: overlap exclusion)"
THRESHOLD = 8
GRAM = THRESHOLD        # the chain unit IS the threshold: a run below THRESHOLD is undetectable, so the two cannot drift
POPULATION = {"corpus_version": "mmlu-pro-v2", "contracts": ["MC_LETTER"]}
OUT_REL = "experiment_results/archv2/induce_rubric_1_audit/overlap_exclusions_split2.json"


def _texts(stem, options_json):
    out = [stem]
    if options_json:
        for o in json.loads(options_json):
            if isinstance(o, str):
                out.append(o)
    return out


def _grams(tokens):
    return [tuple(tokens[i:i + GRAM]) for i in range(len(tokens) - GRAM + 1)]


def eval_index(ev):
    """8-gram -> [(eval text id, position)]; text id -> EVAL variant_id. All corpora, sentinels included."""
    idx, owner = {}, []
    n_var = 0
    for vid, stem, opts in ev.execute("SELECT variant_id, stem, options_sorted_json FROM variant ORDER BY corpus_version,"
                                      " variant_id"):
        n_var += 1
        for t in _texts(stem, opts):
            tid = len(owner)
            owner.append(vid)
            for j, g in enumerate(_grams(I._tokens(t))):
                idx.setdefault(g, []).append((tid, j))
    return idx, owner, n_var


def longest_run(tokens, idx):
    """-> (run in tokens, eval text id) of the longest aligned 8-gram chain of one TRAIN text against one EVAL text."""
    best, best_t = 0, None
    prev = {}
    for g in _grams(tokens):
        cur = {}
        for tid, j in idx.get(g, ()):
            c = prev.get((tid, j - 1), 0) + 1
            cur[(tid, j)] = c
            if c > best or (c == best and best_t is not None and tid < best_t):
                best, best_t = c, tid
        prev = cur
    return (best + GRAM - 1, best_t) if best else (0, None)


def train_candidates(gen):
    side = {i: s for i, s in gen.execute("SELECT item_id, side FROM side")}
    by = {}
    for cv, vid, iid, stem, opts, ct in gen.execute(
            "SELECT corpus_version, variant_id, item_id, stem, options_sorted_json, contract_id FROM variant"):
        if cv == POPULATION["corpus_version"] and ct in POPULATION["contracts"] and side.get(iid) == "TRAIN":
            by.setdefault(vid, (stem, opts))
    return by


def build(gen_path, gen_sha, eval_path, eval_sha, out=print):
    ev = dv2views.open_eval("judge", eval_path, eval_sha)
    try:
        idx, owner, n_ev = eval_index(ev)
    finally:
        ev.close()
    gen = dv2views.open_generation("induce", gen_path, gen_sha)
    try:
        cands = train_candidates(gen)
    finally:
        gen.close()
    excluded = []
    for vid in sorted(cands):
        stem, opts = cands[vid]
        best, best_vid = 0, None
        for t in _texts(stem, opts):
            run, tid = longest_run(I._tokens(t), idx)
            if run and (run > best or (run == best and owner[tid] < best_vid)):
                best, best_vid = run, owner[tid]
        if best >= THRESHOLD:
            excluded.append({"variant_id": vid, "run": best, "eval_variant_id": best_vid})
    rec = {"registration": REGISTRATION, "rule": "exclude a TRAIN candidate sharing >= %d consecutive tokens (aligned %d-gram"
           " chain) with any ONE EVAL text (stem or option; all corpora, sentinels included)" % (THRESHOLD, GRAM),
           "threshold": THRESHOLD, "tokenizer": "judge_v2.induction._tokens (casefold, \\\\w+)", "population": POPULATION,
           "gen_view_sha256_bytes": gen_sha, "eval_view_sha256_bytes": eval_sha, "eval_variants": n_ev,
           "eval_texts": len(owner), "candidates": len(cands), "n_excluded": len(excluded),
           "n_run_ge_50": sum(1 for e in excluded if e["run"] >= 50), "excluded": excluded,
           "audit_blob": "blob:" + git_blob_lf(os.path.abspath(__file__))}
    rec["list_sha256"] = list_sha(rec)
    out("[OVERLAP-AUDIT] eval_view %s (%d variants, %d texts); candidates %d; excluded (run >= %d) %d; run >= 50: %d;"
        " list_sha256 %s" % (os.path.basename(eval_path), n_ev, len(owner), rec["candidates"], THRESHOLD,
                             rec["n_excluded"], rec["n_run_ge_50"], rec["list_sha256"]))
    return rec


def list_sha(rec):
    body = {k: v for k, v in rec.items() if k != "list_sha256"}
    return sha256_text(json.dumps(body, sort_keys=True, ensure_ascii=True))


def write(rec, path):
    if os.path.exists(path):
        refuse("%s exists: the overlap exclusion list is written once" % path)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, sort_keys=True, indent=1, ensure_ascii=True) + "\n")
    return path


def load(path, expect_list_sha, eval_sha, gen_sha):
    """The inducer's ONLY reader: refuses a list whose own sha is not the pinned one, or that was built on another
    eval_view / gen_view, another threshold or another population. Returns the set of excluded TRAIN variant ids."""
    if not os.path.isfile(path):
        refuse("the overlap exclusion list %s is missing (build it with induce_overlap_audit.py --build)" % path)
    rec = json.load(open(path, encoding="utf-8"))
    got = list_sha(rec)
    if got != rec.get("list_sha256") or got != expect_list_sha:
        refuse("the overlap exclusion list's sha %s (recorded %s) is not the pinned %s" % (got, rec.get("list_sha256"),
                                                                                          expect_list_sha))
    if rec.get("eval_view_sha256_bytes") != eval_sha or rec.get("gen_view_sha256_bytes") != gen_sha:
        refuse("the overlap exclusion list was built on eval_view %s / gen_view %s, not %s / %s" % (
            rec.get("eval_view_sha256_bytes"), rec.get("gen_view_sha256_bytes"), eval_sha, gen_sha))
    if rec.get("threshold") != THRESHOLD or rec.get("population") != POPULATION:
        refuse("the overlap exclusion list's threshold %r / population %r are not the ruled ones" % (
            rec.get("threshold"), rec.get("population")))
    return {e["variant_id"] for e in rec["excluded"]}, rec


def main(argv):
    from . import induce_run as R
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--build", action="store_true")
    g.add_argument("--check")
    ap.add_argument("--out", default=os.path.join(ROOT, *OUT_REL.split("/")))
    a = ap.parse_args(argv)
    paths = R.Paths()
    if a.check:
        rec = json.load(open(a.check, encoding="utf-8"))
        print("[OVERLAP-AUDIT] %s: list_sha256 recorded %s, recomputed %s; candidates %s, excluded %s, run >= 50: %s" % (
            a.check, rec.get("list_sha256"), list_sha(rec), rec.get("candidates"), rec.get("n_excluded"),
            rec.get("n_run_ge_50")))
        return 0 if list_sha(rec) == rec.get("list_sha256") else 1
    R.check_manifest(paths, R.GEN_SHA, R.EVAL_SHA)
    rec = build(paths.gen, R.GEN_SHA, paths.eval, R.EVAL_SHA)
    write(rec, a.out)
    print("[OVERLAP-AUDIT] written (mode x): %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
