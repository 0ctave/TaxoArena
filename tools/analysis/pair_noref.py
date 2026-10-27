"""PAIR-NOREF — does the displacement finding hold in the format we actually deploy? (registered 2026-09-14)

  python tools/analysis/pair_noref.py --judge [--pilot N] [--workers 8]
  python tools/analysis/pair_noref.py --analyze

FORMAT-REF's clean reference toggle exists in POINTWISE only, where KEY is +0.258 +- 0.157 and barely
identified; the arena deploys PAIRWISE. This is the same toggle in pairwise: R3's 944 key-decidable matches,
dual order, byte-identical to stack_v2_promptv2_grok.db except that the reference block is removed from the
question and the verify sentence is swapped exactly as pointwise_judge.py does it (VERIFY_REF -> VERIFY_NOREF).
"""
import os, sys, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_p8 as p8
import stack_judge as sj
import prompt_v2
import consensus_fit as cf
import format_ref as fr

CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "pairnoref.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "pairnoref_outcome.txt")
PW_REF = fr.PW_GROK

# The v2 verify block names a supplied reference. Without one the judge must derive the answer itself; this is
# the pairwise twin of pointwise_judge's VERIFY_REF -> VERIFY_NOREF swap, and nothing else in the prompt moves.
REF_SENTENCE = """The question carries a reference solution (marked as produced independently; it may be wrong).
Before critiquing, extract each model's FINAL ANSWER and check it against the reference and
against your own reading of the question."""
NOREF_SENTENCE = """Before critiquing, extract each model's FINAL ANSWER, work out for yourself what the correct
answer should be, and check each model's final answer against it."""


def noref_system_template():
    t = prompt_v2.v2_system_template()
    assert REF_SENTENCE in t, "the v2 reference sentence is not where PAIR-NOREF expects it"
    return t.replace(REF_SENTENCE, NOREF_SENTENCE, 1)


def targets():
    """R3's key-decidable matches, as judged with a reference in stack_v2_promptv2_grok.db."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    K = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in p8.ARENA12: K[q][m] = int(c or 0)
    out = []
    for mid, a, b, qid, anc, w, inv in sqlite3.connect("file:%s?mode=ro" % PW_REF, uri=True).execute(
            "SELECT match_id, model_a, model_b, qid, anchor, winner, invalid FROM verdicts"):
        if inv or qid is None: continue
        if K[qid].get(a) is None or K[qid].get(b) is None: continue
        if K[qid][a] == K[qid][b]: continue
        out.append((mid, qid, a, b, anc))
    return sorted(out), K


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, qid INTEGER, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL)")
    con.commit(); return con


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rubrics = sj.anchor_rubrics()
    tmpl = noref_system_template()
    sched, K = targets()
    if pilot: sched = sched[:pilot]
    con = open_cache()
    done = {m for (m,) in con.execute("SELECT match_id FROM verdicts")}
    todo = [s for s in sched if s[0] not in done]
    evals = rj.load_eval_rows([s[1] for s in sched], {s[2] for s in sched} | {s[3] for s in sched})
    print("PAIR-NOREF: %d key-decidable R3 matches | to do %d (%d calls) | workers %d"
          % (len(sched), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        mid, qid, a, b, anc = job
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None or anc not in rubrics: return None
        sp, rub = rubrics[anc]
        system = tmpl.replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = ra[0]                                       # NO reference block appended
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, ta, tb))[0])
        raw2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, tb, ta))[0])
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, a, b, qid, v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    P, K = fr.evaluation()
    import rejudge_reference as rref
    rref.set_reference("grok-reasoning"); refs = rref.references()
    withref = fr.rows_pairwise(PW_REF, P, K, refs)
    nor = {}
    for mid, a, b, qid, w, inv in open_cache().execute(
            "SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts"):
        if inv: continue
        rl = (refs.get(qid) or ("",))[0]
        pa, pb = P[qid].get(a), P[qid].get(b)
        if pa is None or pb is None: continue
        nor[mid] = (cf.sign_contrast(K[qid].get(a, 0) == 1, K[qid].get(b, 0) == 1),
                    cf.sign_contrast(rl == pa, rl == pb),
                    "A" if w == a else ("B" if w == b else "TIE"))
    common = sorted(set(withref) & set(nor))
    L = ["=== PAIR-NOREF: the reference toggle in the DEPLOYED pairwise format (%d paired matches) ===" % len(common)]
    b1, _ = fr.fit([withref[m] for m in common]); b2, _ = fr.fit([nor[m] for m in common])
    rng = random.Random(7); dk = []; dr = []; dd = []
    for _ in range(600):
        idx = [common[rng.randrange(len(common))] for _ in common]
        x1, _ = fr.fit([withref[m] for m in idx]); x2, _ = fr.fit([nor[m] for m in idx])
        dk.append(x2[1] - x1[1]); dr.append(x2[2] - x1[2]); dd.append((x2[2] - x2[1]) - (x1[2] - x1[1]))
    ci = lambda v: (sorted(v)[15], sorted(v)[584])
    L.append("")
    L.append("  (1)(2) the signed-contrast fit, paired:")
    L.append("      pairwise WITH a reference   KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (b1[1], b1[2], b1[2] - b1[1]))
    L.append("      pairwise WITHOUT one        KEY %+.3f | REF %+.3f | REF-KEY %+.3f" % (b2[1], b2[2], b2[2] - b2[1]))
    for lbl, v, d in (("KEY", dk, b2[1] - b1[1]), ("REF", dr, b2[2] - b1[2]), ("REF-KEY", dd, (b2[2] - b2[1]) - (b1[2] - b1[1]))):
        lo, hi = ci(v)
        L.append("      delta %-8s %+.3f  95%% CI [%+.3f, %+.3f]%s" % (lbl, d, lo, hi, "" if lo < 0 < hi else "   <- excludes zero"))
    # the registered primary is stated the other way round: removing the reference RAISES key weight
    lo, hi = ci(dk)
    disp = lo > 0
    L.append("")
    L.append("  (1) PRIMARY: displacement replicates if the judge weights correctness LESS when a reference is")
    L.append("      present, i.e. delta KEY (noref minus withref) is POSITIVE with a CI excluding zero.")
    L.append("      delta KEY %+.3f [%+.3f, %+.3f] -> %s" % (b2[1] - b1[1], lo, hi,
             "DISPLACEMENT REPLICATES in the deployed format" if disp else
             "NOT replicated: the displacement finding is pointwise-only and the paper must narrow the claim"))
    L.append("      pointwise, for comparison: KEY +0.817 without a reference, +0.257 with one (delta -0.560)")
    # (3) accuracy and (4) ties
    def acc_ties(d):
        n = len(d); t = sum(1 for m in d if d[m][2] == "TIE")
        c = sum(1 for m in d if (d[m][2] == "A" and d[m][0] > 0) or (d[m][2] == "B" and d[m][0] < 0))
        return c / n, t / n
    aw, tw = acc_ties({m: withref[m] for m in common}); an, tn = acc_ties({m: nor[m] for m in common})
    b = sum(1 for m in common if ((withref[m][2] == "A" and withref[m][0] > 0) or (withref[m][2] == "B" and withref[m][0] < 0))
            and not ((nor[m][2] == "A" and nor[m][0] > 0) or (nor[m][2] == "B" and nor[m][0] < 0)))
    c_ = sum(1 for m in common if ((nor[m][2] == "A" and nor[m][0] > 0) or (nor[m][2] == "B" and nor[m][0] < 0))
             and not ((withref[m][2] == "A" and withref[m][0] > 0) or (withref[m][2] == "B" and withref[m][0] < 0)))
    L.append("")
    L.append("  (3) THE CLEAN PAIRWISE REFERENCE EFFECT ON ACCURACY: with %.3f | without %.3f | %+.3f (%d:%d, McNemar p=%.4g)"
             % (aw, an, aw - an, b, c_, p8.mcn(b, c_)))
    L.append("      against the confounded +11.8pp in the POINTWISE 2x2 row (v1 prompt + cell rubric comparator)")
    L.append("      and J2-R's clean +7.6pp on a different judge.")
    L.append("  (4) TIE RATE: with a reference %.3f | without %.3f (%+.3f)" % (tw, tn, tn - tw))
    # ties are scored as errors, so (3) mixes discrimination with abstention - the RK-1b lesson, applied here
    def committed(d):
        c = [m for m in common if d[m][2] != "TIE"]
        return len(c), sum(1 for m in c if (d[m][2] == "A" and d[m][0] > 0) or (d[m][2] == "B" and d[m][0] < 0)) / max(1, len(c))
    nw, cw = committed(withref); nn, cn = committed(nor)
    L.append("      DECOMPOSITION, since ties score as errors: accuracy on the verdicts the judge COMMITS to is")
    L.append("      %.3f with a reference (n=%d) and %.3f without (n=%d), a gap of %+.3f against the %+.3f headline."
             % (cw, nw, cn, nn, cw - cn, aw - an))
    L.append("      So %.0f%% of the reference's apparent accuracy effect is the judge ABSTAINING less, and %.0f%% is"
             % (100 * (1 - (cw - cn) / (aw - an)), 100 * (cw - cn) / (aw - an)))
    L.append("      better discrimination - the same split RK-1b turned out to have, and the same one AGGREGATE exploits.")
    lo_k, hi_k = ci(dk)
    L.append("")
    L.append("  IS PAIRWISE GENUINELY DIFFERENT FROM POINTWISE, or just underpowered here? The pointwise toggle gave")
    L.append("      delta KEY -0.560; this CI is [%+.3f, %+.3f], which %s it. The formats differ, they are not merely"
             % (lo_k, hi_k, "EXCLUDES" if not (lo_k <= -0.560 <= hi_k) else "CONTAINS"))
    L.append("      indistinguishable at this sample size.")
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
