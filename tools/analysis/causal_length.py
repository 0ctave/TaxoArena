"""L1 — causal length test (docs/s_l_series_registration.md, registered before any call).

R2 live top-4 key-decidable matches where the CORRECT answer is longer by >= 300 chars.
Arms (same session, Mistral-Large-3, byte-identical v1 prompts, dual order):
  original  — traces as judged in R2
  truncate  — correct answer cut at the last sentence boundary <= the wrong answer's length,
              before the RESOLVED selected-answer line is appended
  pad       — wrong answer padded to the correct answer's length with a content-free filler
Primary: original > truncate (paired McNemar). Secondary: original > pad.

  python tools/analysis/causal_length.py [--judge mistral|grok-reasoning] [--workers N] [--pilot N]
  python tools/analysis/causal_length.py --analyze
"""
import os, sys, re, json, time, math, csv, sqlite3, argparse, threading, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import judge_free_tests as jf

JUDGES = {"mistral": ("Mistral-Large-3", "AZURE_AI_API_KEY"), "grok-reasoning": ("grok-4-1-fast-reasoning", "AZURE_GROK_API_KEY")}
OUT_DIR = os.path.join(ROOT, "experiment_results", "causal_length")
THR = 300
FILLER = ("Before concluding, it is worth restating that the approach taken above follows the standard "
          "procedure for this class of problem: each intermediate quantity was checked for consistency with "
          "the given information, alternative readings of the question were considered and set aside where "
          "they did not change the outcome, and the final selection is the option best supported by the "
          "reasoning presented. ")
ARMS = ("original", "truncate", "pad")
ENDPOINT = KEY = MODEL = None
REFERENCE = None   # --reference grok-reasoning = L1-V (docs/judge_v2_program.md): every arm's question carries the J2-R reference
PROMPT = "v1"      # --prompt v2 = L1-V2: the v2 SYSTEM mechanics (prompt_v2.build_system_prompt_v2) on top of the reference


def load_env(judge):
    global ENDPOINT, KEY, MODEL
    MODEL, key_name = JUDGES[judge]
    kv = {}
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        line = line.strip().replace("\r", "")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            kv[k] = v
    ENDPOINT = kv["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    KEY = kv[key_name]


def call(system, user, retries=6):
    body = json.dumps({"model": MODEL, "max_tokens": 8192 if "reasoning" in MODEL else 2048,
                       "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(ENDPOINT, data=body, method="POST", headers={"Content-Type": "application/json", "api-key": KEY})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                p = json.loads(r.read().decode("utf-8"))
            return p["choices"][0]["message"].get("content") or ""
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 504) and attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < retries - 1:
                time.sleep(min(2 ** attempt * 3, 60)); continue
            raise
    raise RuntimeError("unreachable")


def eligible():
    """(qid, node_id, correct_model, wrong_model) for R2 live top-4 decidable matches, correct longer by >= THR."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G, L = {}, {}
    for q, m, c, ln in ev.execute("SELECT question_id, model_name, is_correct, length(model_output) FROM eval_results"):
        if m in jf.TOP4:
            G[(q, m)] = bool(c); L[(q, m)] = ln or 0
    out = {}
    with open(jf.R2, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Rationale"].startswith("Reconstructed"):
                continue
            a, b, q = r["ModelA"], r["ModelB"], int(r["QueryId"])
            if a not in jf.TOP4 or b not in jf.TOP4:
                continue
            ca, cb = G.get((q, a)), G.get((q, b))
            if ca is None or cb is None or ca == cb:
                continue
            cm, wm = (a, b) if ca else (b, a)
            if L[(q, cm)] - L[(q, wm)] >= THR:
                out[(q, cm, wm)] = r["NodeId"]
    return out


def truncate_to(text, limit):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    m = max(cut.rfind(". "), cut.rfind(".\n"), cut.rfind("! "), cut.rfind("? "))
    return cut[:m + 1] if m > limit * 0.5 else cut


def pad_to(text, target):
    while len(text) < target:
        text = text.rstrip() + "\n\n" + FILLER
    return text


def open_cache(judge):
    os.makedirs(OUT_DIR, exist_ok=True)
    name = judge if REFERENCE is None else "%s_ref%s" % (judge, REFERENCE.replace("-reasoning", "").replace("-", ""))
    if PROMPT == "v2": name += "_v2"
    con = sqlite3.connect(os.path.join(OUT_DIR, "%s.db" % name))
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (qid INTEGER, cm TEXT, wm TEXT, arm TEXT, node_id TEXT, "
                "len_c INTEGER, len_w INTEGER, vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, "
                "raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (qid, cm, wm, arm))")
    con.commit()
    return con


def run(judge, workers, pilot):
    load_env(judge)
    nodes = rj.load_nodes()
    matches = eligible()
    keys = sorted(matches)
    if pilot:
        keys = keys[:pilot]
    evals = rj.load_eval_rows([q for q, _, _ in keys], {m for _, a, b in keys for m in (a, b)})
    cache = open_cache(judge)
    done = {(r[0], r[1], r[2], r[3]) for r in cache.execute("SELECT qid, cm, wm, arm FROM verdicts")}
    todo = [(k, arm) for k in keys for arm in ARMS if (k[0], k[1], k[2], arm) not in done]
    refs = None
    if REFERENCE is not None:
        import rejudge_reference as rref
        rref.set_reference(REFERENCE); refs = rref.references()
        todo = [(k, arm) for k, arm in todo if k[0] in refs]
    print("judge=%s | reference=%s | eligible matches %d | jobs %d (%d calls) | workers %d" % (judge, REFERENCE, len(keys), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock()
    ok = err = 0

    def one(k, arm):
        q, cm, wm = k
        rc, rw = evals[(q, cm)], evals[(q, wm)]
        qtext = rc[0]
        if refs is not None:
            import rejudge_reference as rref
            qtext = rref.with_reference(qtext, refs[q])
        oc, ow = rj.unwrap_envelope(rc[2] or "") if rc[2] else "", rj.unwrap_envelope(rw[2] or "") if rw[2] else ""
        if arm == "truncate":
            oc = truncate_to(oc, len(ow))
        elif arm == "pad":
            ow = pad_to(ow, len(oc))
        tc = rj.maybe_resolve(oc, rc[3], rc[1]) if oc.strip() else rj.robust_trace(rc[2], rc[3], rc[1])
        tw = rj.maybe_resolve(ow, rw[3], rw[1]) if ow.strip() else rj.robust_trace(rw[2], rw[3], rw[1])
        if PROMPT == "v2":
            import prompt_v2
            system = prompt_v2.build_system_prompt_v2(nodes[matches[k]])
        else:
            system = rj.build_system_prompt(nodes[matches[k]])
        # presentation: correct model as A in order 1 (the arena's own A/B is arbitrary; we
        # keep the same convention across arms so the dual-order combination is comparable)
        raw1 = call(system, rj.build_user_prompt(qtext, tc, tw))
        raw2 = call(system, rj.build_user_prompt(qtext, tw, tc))
        v1, _ = rj.parse_judge(re.sub(r"<think>.*?</think>", "", raw1, flags=re.S))
        v2, _ = rj.parse_judge(re.sub(r"<think>.*?</think>", "", raw2, flags=re.S))
        w, flip, inv = rj.combine_orders(v1, v2)
        w_name = {"Model A": cm, "Model B": wm}.get(w, w)
        return (q, cm, wm, arm, matches[k], len(tc), len(tw), v1, v2, w_name, int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, k, arm): (k, arm) for k, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try:
                row = f.result()
            except Exception as e:
                err += 1
                print("  ERROR %s: %s" % (futs[f], str(e)[:140]), flush=True)
                continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 15), row)
                cache.commit()
            ok += 1
            if i % 30 == 0 or i == len(todo):
                print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    print("done: ok %d, errors %d" % (ok, err), flush=True)


def mcnemar_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, i) * 0.5 ** n for i in range(k + 1)))


def analyze():
    names = list(JUDGES) + [j + "_refgrok" for j in JUDGES] + [j + "_refgrok_v2" for j in JUDGES]
    for judge in names:
        p = os.path.join(OUT_DIR, "%s.db" % judge)
        if not os.path.exists(p):
            continue
        c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
        rows = defaultdict(dict)
        for q, cm, wm, arm, w, inv, lc, lw in c.execute("SELECT qid, cm, wm, arm, winner, invalid, len_c, len_w FROM verdicts"):
            if not inv:
                rows[(q, cm, wm)][arm] = (w == cm, lc, lw)
        full = {k: v for k, v in rows.items() if all(a in v for a in ARMS)}
        if not full:
            print("[%s] no complete triples yet" % judge); continue
        print("=== L1%s [%s]: %d matches with all three arms ===" % ("-V2" if "_v2" in judge else ("-V" if "_ref" in judge else ""), judge, len(full)))
        for arm in ARMS:
            acc = sum(v[arm][0] for v in full.values()) / len(full)
            lc = sum(v[arm][1] for v in full.values()) / len(full); lw = sum(v[arm][2] for v in full.values()) / len(full)
            print("  %-9s correct-verdict rate %.3f | mean len correct %.0f wrong %.0f" % (arm, acc, lc, lw))
        for arm, tag in (("truncate", "REGISTERED PRIMARY"), ("pad", "SECONDARY")):
            b = sum(1 for v in full.values() if v["original"][0] and not v[arm][0])
            cc = sum(1 for v in full.values() if v[arm][0] and not v["original"][0])
            p_ = mcnemar_p(b, cc)
            drop = (sum(v["original"][0] for v in full.values()) - sum(v[arm][0] for v in full.values())) / len(full)
            print("  original vs %-8s drop %+.3f | discordant orig-only %d vs %s-only %d | McNemar p=%.4f -> %s (%s)"
                  % (arm, drop, b, arm, cc, p_, "PASS" if (drop > 0 and p_ < 0.05) else "FAIL", tag))
        if "_ref" in judge:
            tr = sum(v["truncate"][0] for v in full.values()) / len(full); orig = sum(v["original"][0] for v in full.values()) / len(full)
            pad = sum(v["pad"][0] for v in full.values()) / len(full)
            print("  L1-V REGISTERED PRIMARY (truncation drop <= 0.25 AND truncate arm >= 0.55; L1 was -0.507 / 0.259): drop %+.3f, truncate %.3f -> %s"
                  % (orig - tr, tr, "PASS" if (orig - tr <= 0.25 and tr >= 0.55) else "FAIL"))
            print("  L1-V SECONDARY (pad within +/-0.03 of original): pad %.3f vs original %.3f -> %s" % (pad, orig, "PASS" if abs(pad - orig) <= 0.03 else "FAIL"))


def analyze_v2_vs_v1():
    pa, pb = os.path.join(OUT_DIR, "mistral_refgrok.db"), os.path.join(OUT_DIR, "mistral_refgrok_v2.db")
    if not (os.path.exists(pa) and os.path.exists(pb)): return
    def load(p):
        c = sqlite3.connect("file:%s?mode=ro" % p, uri=True); out = defaultdict(dict)
        for q, cm, wm, arm, w, inv in c.execute("SELECT qid, cm, wm, arm, winner, invalid FROM verdicts"):
            if not inv: out[(q, cm, wm)][arm] = (w == cm)
        return out
    A, B = load(pa), load(pb)
    common = [k for k in A if k in B and all(a in A[k] and a in B[k] for a in ARMS)]
    if not common: return
    print("=== L1-V2 vs L1-V (same matches, %d): v2 mechanics + reference vs v1 + reference ===" % len(common))
    for arm in ARMS:
        b = sum(1 for k in common if B[k][arm] and not A[k][arm]); c = sum(1 for k in common if A[k][arm] and not B[k][arm])
        ra = sum(A[k][arm] for k in common) / len(common); rb = sum(B[k][arm] for k in common) / len(common)
        tag = ""
        if arm == "truncate": tag = "  -> L1-V2 REGISTERED PRIMARY %s" % ("PASS" if (rb > ra and mcnemar_p(b, c) < 0.05) else "FAIL")
        if arm == "original": tag = "  -> secondary (>= v1 - 0.02) %s" % ("OK" if rb >= ra - 0.02 else "FAIL")
        print("  %-9s v2 %.3f vs v1 %.3f (%+.3f) | %d:%d | p=%.4f%s" % (arm, rb, ra, rb - ra, b, c, mcnemar_p(b, c), tag))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", choices=list(JUDGES), default="mistral")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--reference", choices=["grok-reasoning"], default=None)
    ap.add_argument("--prompt", choices=["v1", "v2"], default="v1")
    a = ap.parse_args()
    REFERENCE = a.reference
    PROMPT = a.prompt
    if a.analyze:
        analyze(); analyze_v2_vs_v1()
    else:
        run(a.judge, a.workers, a.pilot)
        analyze(); analyze_v2_vs_v1()
