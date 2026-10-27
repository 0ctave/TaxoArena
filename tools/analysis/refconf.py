"""REF-CONF — a reference that reports its own confidence (registered 2026-09-10 15:30, docs/judge_v2_program.md).

  python tools/analysis/refconf.py --gate                 # FREE CHECK: is the self-reported confidence informative?
  python tools/analysis/refconf.py --judge [--pilot N] [--workers N] [--judge-model grok|mistral]
  python tools/analysis/refconf.py --analyze [--judge-model grok|mistral]

Gate (registered): AUC(confidence, key-correct) >= 0.65 AND acc(conf >= 90) - acc(conf < 70) >= 15pp; else the judging
half is cancelled. Judging: STACK-v2 with the NEW reference shown WITHOUT its confidence (base) vs WITH it (conf),
both arms fresh and interleaved on R3's 1,980 matches. PRIMARY: conf > base on key-decidable, paired McNemar p < 0.05.
SECONDARY: on ref-WRONG pairs conf beats base by >= 3pp while on ref-correct pairs it loses < 1pp.
"""
import os, sys, json, time, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_p8 as p8
import stack_judge as sj
import prompt_v2

CONF_DB = os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning_conf.db")
JUDGE = "grok"


def cache_path():
    return os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refconf_%s.db" % JUDGE)


def conf_references():
    """qid -> (letter, option text, correct, confidence)."""
    s = sqlite3.connect("file:%s?mode=ro" % CONF_DB, uri=True)
    ans = {q: (a, c, cf) for q, a, c, cf in s.execute("SELECT question_id, answer, correct, confidence FROM answers WHERE answer != '' AND confidence IS NOT NULL")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = {}
    for q, (a, c, cf) in ans.items():
        r = ev.execute("SELECT options_json FROM eval_results WHERE question_id=? AND model_name='gpt-4o-2024-08-06'", (q,)).fetchone()
        opts = json.loads(r[0]) if r and r[0] else []
        i = "ABCDEFGHIJ".find(a)
        out[q] = (a, opts[i] if 0 <= i < len(opts) else "", bool(c), float(cf))
    return out


def auc(pos, neg):
    """Mann-Whitney AUC with tie correction."""
    n = 0.0
    for p in pos:
        for q in neg:
            n += 1.0 if p > q else (0.5 if p == q else 0.0)
    return n / (len(pos) * len(neg))


def gate():
    refs = conf_references()
    correct = [r[3] for r in refs.values() if r[2]]; wrong = [r[3] for r in refs.values() if not r[2]]
    a = auc(correct, wrong)
    hi = [r for r in refs.values() if r[3] >= 90]; lo = [r for r in refs.values() if r[3] < 70]
    acc_hi = sum(r[2] for r in hi) / max(1, len(hi)); acc_lo = sum(r[2] for r in lo) / max(1, len(lo))
    print("=== REF-CONF gate: %d references with confidence (accuracy %.3f) ===" % (len(refs), sum(r[2] for r in refs.values()) / len(refs)))
    print("  AUC(confidence -> key-correct) = %.3f (bar 0.65)" % a)
    print("  accuracy at conf >= 90: %.3f (n=%d) | at conf < 70: %.3f (n=%d) | gap %+.3f (bar +0.15)" % (acc_hi, len(hi), acc_lo, len(lo), acc_hi - acc_lo))
    bins = defaultdict(list)
    for r in refs.values(): bins[min(100, int(r[3] // 10) * 10)].append(r[2])
    for b in sorted(bins): print("    conf %3d-%3d: n=%4d acc %.3f" % (b, b + 9 if b < 100 else 100, len(bins[b]), sum(bins[b]) / len(bins[b])))
    ok = a >= 0.65 and acc_hi - acc_lo >= 0.15
    print("  GATE: %s" % ("PASS -> judging half proceeds" if ok else "FAIL -> judging half cancelled"))
    return ok


def with_conf(query, ref, show):
    letter, text, _, cf = ref
    if not show:
        return query + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (letter, text)
    return query + ("\n\n[Reference solution — produced independently, may be wrong; the solver's self-reported confidence is %d%%. "
                    "Treat a low-confidence reference as a hint to verify, not as an answer key]\n(%s) %s" % (int(round(cf)), letter, text))


def open_cache():
    con = sqlite3.connect(cache_path())
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, ref_letter TEXT, "
                "ref_correct INTEGER, ref_conf REAL, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, "
                "PRIMARY KEY (match_id, arm))")
    con.commit(); return con


def judge_call(system, user):
    if JUDGE == "grok":
        return rr.strip_think(rr.call_judge(system, user)[0])
    return p8.call(system, user)


def judge(pilot, workers):
    p8.load_env()
    if JUDGE == "grok":
        rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    refs = conf_references(); rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    sample = rj.sample_matches()
    if pilot: sample = sample[:pilot]
    cache = open_cache(); done = {(m, a) for m, a in cache.execute("SELECT match_id, arm FROM verdicts")}
    todo = [(m, arm) for m in sample for arm in ("base", "conf") if (m[0], arm) not in done]
    evals = rj.load_eval_rows([int(m[1]) for m, _ in todo], {m[2] for m, _ in todo} | {m[3] for m, _ in todo})
    print("REF-CONF [judge=%s]: sample %d | jobs %d (%d calls) | refs %d | workers %d" % (JUDGE, len(sample), len(todo), 2 * len(todo), len(refs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m, arm):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb, ref, anc = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid)
        if ra is None or rb is None or ref is None or anc is None: return None
        sp, rb_ = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rb_) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = with_conf(ra[0], ref, arm == "conf")
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = judge_call(system, rj.build_user_prompt(q, ta, tb)); raw2 = judge_call(system, rj.build_user_prompt(q, tb, ta))
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, arm, a, b, qid, anc, ref[0], int(ref[2]), ref[3], v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, arm): (m, arm) for m, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 19), row); cache.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    cache = open_cache(); V = defaultdict(dict)
    for mid, arm, a, b, q, anc, rc, cf, w, inv in cache.execute("SELECT match_id, arm, model_a, model_b, qid, anchor, ref_correct, ref_conf, winner, invalid FROM verdicts"):
        if not inv: V[mid][arm] = (w, a, b, q, anc, bool(rc), cf)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = {}
    for mid, arms in V.items():
        if "base" not in arms or "conf" not in arms: continue
        w, a, b, q, anc, rc, cf = arms["conf"]; ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = {"conf": w == d, "base": arms["base"][0] == d, "rc": rc, "cf": cf, "top": a in sj.TOP4 and b in sj.TOP4}

    def stats(ks):
        n = len(ks); pc = sum(rows[k]["conf"] for k in ks) / max(1, n); pb = sum(rows[k]["base"] for k in ks) / max(1, n)
        b = sum(rows[k]["conf"] and not rows[k]["base"] for k in ks); c = sum(rows[k]["base"] and not rows[k]["conf"] for k in ks)
        return n, pc, pb, b, c, p8.mcn(b, c)
    keys = list(rows); n, pc, pb, b, c, p = stats(keys)
    print("=== REF-CONF: reference shown WITH vs WITHOUT its self-reported confidence (both fresh), %s, %d key-decidable paired ===" % ("grok-4-1-fast-non-reasoning" if JUDGE == "grok" else "Mistral", n))
    print("  ALL          conf %.3f vs base %.3f (%+.3f) | %d:%d | p=%.4f -> PRIMARY %s" % (pc, pb, pc - pb, b, c, p, "PASS" if (pc > pb and p < 0.05) else "FAIL"))
    rw = stats([k for k in keys if not rows[k]["rc"]]); rc_ = stats([k for k in keys if rows[k]["rc"]])
    print("  ref-WRONG    n=%4d conf %.3f vs base %.3f (%+.3f) %d:%d p=%.4f" % (rw[0], rw[1], rw[2], rw[1] - rw[2], rw[3], rw[4], rw[5]))
    print("  ref-correct  n=%4d conf %.3f vs base %.3f (%+.3f) %d:%d p=%.4f" % (rc_[0], rc_[1], rc_[2], rc_[1] - rc_[2], rc_[3], rc_[4], rc_[5]))
    print("  SECONDARY (ref-wrong gain >= +3pp AND ref-correct loss < 1pp): %s" % ("PASS" if (rw[1] - rw[2] >= 0.03 and rc_[2] - rc_[1] < 0.01) else "FAIL"))
    t = stats([k for k in keys if rows[k]["top"]]); print("  top cluster  n=%4d conf %.3f vs base %.3f (%+.3f) %d:%d p=%.4f" % (t[0], t[1], t[2], t[1] - t[2], t[3], t[4], t[5]))
    for lab, sel in (("conf < 70", lambda r: r["cf"] < 70), ("70-89", lambda r: 70 <= r["cf"] < 90), ("conf >= 90", lambda r: r["cf"] >= 90)):
        s_ = stats([k for k in keys if sel(rows[k])]); print("    %-10s n=%4d conf %.3f vs base %.3f (%+.3f) %d:%d" % (lab, s_[0], s_[1], s_[2], s_[1] - s_[2], s_[3], s_[4]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true"); ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--judge-model", choices=["grok", "mistral"], default="grok")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(); JUDGE = a.judge_model
    if a.gate: gate()
    elif a.judge: judge(a.pilot, a.workers); analyze()
    elif a.analyze: analyze()
