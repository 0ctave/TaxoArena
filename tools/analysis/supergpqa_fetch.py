"""SUPERGPQA-STAGE0 (RP11) fetcher: download the WHITELISTED SuperGPQA files outside git, verify
every file against the Hub's LFS sha256, and write a sha256 manifest. ZERO judge calls.

Registration: docs/judge_v2_program.md, section "## Registered 2026-09-27 (before any code or
call) — SUPERGPQA-STAGE0 ..." (L21790-L21829 as of a357ef0). THE SEAL: any SuperGPQA-Records file
whose content aggregates over questions (results_*.json / results_*.xlsx, per-model /
per-discipline accuracies) is NEVER fetched, never opened. This script decides what to fetch from
the Hub's FILE LIST (names and sizes) only, and it REFUSES (exit 3) if a whitelisted name matches
the seal pattern or if the list offers a name it cannot classify.

What is fetched (the whitelist):
  m-a-p/SuperGPQA           README.md, SuperGPQA-all.jsonl           (questions + hierarchy + key)
  m-a-p/SuperGPQA-Records   README.md, zero-shot/<model>_SuperGPQA-all_zero-shot.jsonl (49 files)
Five-shot (26 base models) and zero-shot-bon (64 files) are NOT fetched by default (stage 0's
two-roster contrast and best-of-N floor are DESCRIPTIVE; --with-five-shot / --with-bon add them,
same seal).

Both repos are pinned by their Hub commit sha (REVISIONS below); a changed revision is fatal.
Target: Z:/FAC/TUBerlin/THESIS/TaxoArena_data/supergpqa/ (outside git). Manifest:
<target>/MANIFEST_supergpqa_fetch.json (per file: repo, revision, path, bytes, sha256, the Hub's
LFS oid, retrieval time). Resumable: a file already present whose sha256 equals the LFS oid is
kept; a mismatch is re-downloaded once, then fatal.

Launch:  python tools/analysis/supergpqa_fetch.py --list      (file list + seal check, no download)
         python tools/analysis/supergpqa_fetch.py --fetch     (download + verify + manifest)
         python tools/analysis/supergpqa_fetch.py --selftest  (seal classifier on synthetic names)
"""
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request

TARGET = os.environ.get("SUPERGPQA_DATA", "Z:/FAC/TUBerlin/THESIS/TaxoArena_data/supergpqa")
REVISIONS = {
    "m-a-p/SuperGPQA": "4430d4458112c7d4497fdcf94d7cc223313d6acf",
    "m-a-p/SuperGPQA-Records": "d52d0a8bdb2ae86733fb6085aa1ec54085fffbec",
}
QUESTION_FILE = "SuperGPQA-all.jsonl"
ZS_RE = re.compile(r"^zero-shot/([A-Za-z0-9._\-]+)_SuperGPQA-all_zero-shot\.jsonl$")
FS_RE = re.compile(r"^five-shot/([A-Za-z0-9._\-]+)_SuperGPQA-all_five-shot\.jsonl$")
BON_RE = re.compile(r"^zero-shot-bon/([A-Za-z0-9._\-]+)_SuperGPQA-all_zero-shot_([0-9]+)\.jsonl$")
# THE SEAL: aggregate files. Matched on the NAME; never opened.
SEAL_RE = re.compile(r"(^|/)results_[^/]*$|\.xlsx$|(^|/)[^/]*(summary|leaderboard|aggregate|accurac)[^/]*$", re.I)


def classify(repo, path):
    """-> 'sealed' | 'question' | 'card' | 'zero-shot' | 'five-shot' | 'bon' | 'meta' | 'unknown'."""
    if SEAL_RE.search(path):
        return "sealed"
    if path == "README.md":
        return "card"
    if path == ".gitattributes":
        return "meta"
    if repo == "m-a-p/SuperGPQA":
        return "question" if path == QUESTION_FILE else "unknown"
    if ZS_RE.match(path):
        return "zero-shot"
    if FS_RE.match(path):
        return "five-shot"
    if BON_RE.match(path):
        return "bon"
    return "unknown"


def hub_tree(repo, rev):
    url = "https://huggingface.co/api/datasets/%s/tree/%s?recursive=true" % (repo, rev)
    with urllib.request.urlopen(url, timeout=120) as r:
        return [x for x in json.load(r) if x.get("type") == "file"]


def hub_sha(repo):
    with urllib.request.urlopen("https://huggingface.co/api/datasets/%s" % repo, timeout=60) as r:
        return json.load(r).get("sha")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def plan(with_five_shot=False, with_bon=False):
    want = {"question", "card", "zero-shot"} | ({"five-shot"} if with_five_shot else set()) | ({"bon"} if with_bon else set())
    out, counts, unknown = [], {}, []
    for repo, rev in REVISIONS.items():
        live = hub_sha(repo)
        if live != rev:
            raise SystemExit("[FETCH] REFUSED: %s revision drift: pinned %s, Hub head %s" % (repo, rev, live))
        for x in hub_tree(repo, rev):
            k = classify(repo, x["path"])
            counts[(repo, k)] = counts.get((repo, k), 0) + 1
            if k == "unknown":
                unknown.append((repo, x["path"]))
            if k in want:
                if k == "sealed":
                    raise SystemExit("[FETCH] REFUSED: sealed file in the whitelist: %s" % x["path"])
                oid = (x.get("lfs") or {}).get("oid")
                out.append({"repo": repo, "revision": rev, "path": x["path"], "kind": k,
                            "bytes": int((x.get("lfs") or {}).get("size", x.get("size", 0))), "lfs_oid": oid})
    if unknown:
        raise SystemExit("[FETCH] REFUSED: unclassified names in the file list: %r" % unknown[:10])
    return out, counts


def fetch_one(e):
    dst = os.path.join(TARGET, e["repo"].split("/")[1], *e["path"].split("/"))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    for attempt in (1, 2):
        if os.path.exists(dst):
            s = sha256_file(dst)
            if e["lfs_oid"] is None or s == e["lfs_oid"]:
                return dst, s, "kept" if attempt == 1 else "fetched"
            os.remove(dst)
        url = "https://huggingface.co/datasets/%s/resolve/%s/%s" % (e["repo"], e["revision"], e["path"])
        tmp = dst + ".part"
        with urllib.request.urlopen(url, timeout=600) as r, open(tmp, "wb") as f:
            for b in iter(lambda: r.read(1 << 20), b""):
                f.write(b)
        os.replace(tmp, dst)
    s = sha256_file(dst)
    if e["lfs_oid"] is not None and s != e["lfs_oid"]:
        raise SystemExit("[FETCH] REFUSED: sha256 mismatch after re-download: %s" % dst)
    return dst, s, "fetched"


def selftest():
    cases = [
        ("m-a-p/SuperGPQA-Records", "zero-shot/results_SuperGPQA-all_all_models.json", "sealed"),
        ("m-a-p/SuperGPQA-Records", "zero-shot/results_SuperGPQA-all_all_models.xlsx", "sealed"),
        ("m-a-p/SuperGPQA-Records", "five-shot/results_SuperGPQA-all_all_models.json", "sealed"),
        ("m-a-p/SuperGPQA-Records", "zero-shot-bon/model_summary.json", "sealed"),
        ("m-a-p/SuperGPQA-Records", "zero-shot/o1-2024-12-17_SuperGPQA-all_zero-shot.jsonl", "zero-shot"),
        ("m-a-p/SuperGPQA-Records", "five-shot/K2_SuperGPQA-all_five-shot.jsonl", "five-shot"),
        ("m-a-p/SuperGPQA-Records", "zero-shot-bon/QwQ_SuperGPQA-all_zero-shot_12.jsonl", "bon"),
        ("m-a-p/SuperGPQA-Records", "zero-shot/weird.bin", "unknown"),
        ("m-a-p/SuperGPQA", "SuperGPQA-all.jsonl", "question"),
        ("m-a-p/SuperGPQA", "README.md", "card"),
        ("m-a-p/SuperGPQA", "other.jsonl", "unknown"),
    ]
    n = 0
    for repo, p, want in cases:
        got = classify(repo, p)
        assert got == want, (p, got, want)
        n += 1
    print("supergpqa_fetch selftest: %d/%d classifier cases OK (seal on name only)" % (n, len(cases)))
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if not ({"--list", "--fetch"} & set(argv)):
        print(__doc__)
        return 2
    entries, counts = plan("--with-five-shot" in argv, "--with-bon" in argv)
    for (repo, k), c in sorted(counts.items()):
        print("[FETCH] list %-26s %-10s %d" % (repo, k, c))
    print("[FETCH] whitelist %d files, %.3f GB; sealed files are listed by count only and never fetched"
          % (len(entries), sum(e["bytes"] for e in entries) / 1e9))
    if "--fetch" not in argv:
        return 0
    man = {"target": TARGET, "revisions": REVISIONS, "files": []}
    mpath = os.path.join(TARGET, "MANIFEST_supergpqa_fetch.json")
    for i, e in enumerate(entries, 1):
        dst, s, how = fetch_one(e)
        row = dict(e, local=dst, sha256=s, how=how,
                   retrieved_utc=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
        man["files"].append(row)
        print("[FETCH] %3d/%d %s sha256=%s bytes=%d %s" % (i, len(entries), e["path"], s, os.path.getsize(dst), how), flush=True)
        with open(mpath + ".tmp", "w", encoding="utf-8", newline="\n") as f:
            json.dump(man, f, indent=1)
        os.replace(mpath + ".tmp", mpath)
    print("[FETCH] DONE %d files; manifest %s sha256=%s" % (len(entries), mpath, sha256_file(mpath)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
