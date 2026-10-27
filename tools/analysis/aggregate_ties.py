"""AGGREGATE — the tie rule is the largest untested lever (registered 2026-09-14)

  python tools/analysis/aggregate_ties.py --judge [--pilot N] [--workers 6]
  python tools/analysis/aggregate_ties.py --analyze

ORACLE found the judge right on 0.929 of the verdicts it COMMITS to, with 49 of its 67 remaining errors being
dual-order TIES that are concentrated on the questions separating the pair. Only the tied questions are touched
here, under both reference conditions already cached, with two tie-breaks that are ORDER-SYMMETRIC (unlike
keeping one order, which is not a rule anyone could ship):

  REPLICATE  two further pairwise calls, one per order -> majority of four verdicts, 2-2 stays TIE
  GRADE      pointwise grades for both answers -> higher grade wins, equal grades stay TIE
"""
import os, sys, time, sqlite3, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import stack_judge as sj
import pointwise_judge as pt
import prompt_v2
import arxiask_probe as ax
import oracle_ref as orc

A, B = ax.A, ax.B
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "aggregate.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "aggregate_outcome.txt")
SRC = {"grok": ax.CACHE, "oracle": orc.CACHE}


def canon(vote, order):
    """A canonical winner from a raw vote. Order 2 presents B first, so its vote inverts."""
    m = {"Model A": A, "Model B": B} if order == 1 else {"Model A": B, "Model B": A}
    return m.get(vote)


def tied(cond):
    """The questions the registered run returned a TIE on, with their two original raw votes."""
    out = {}
    for q, v1, v2, w, inv in sqlite3.connect("file:%s?mode=ro" % SRC[cond], uri=True).execute(
            "SELECT qid, vote1, vote2_raw, winner, invalid FROM pairwise"):
        if inv or w != "TIE": continue
        out[q] = (v1, v2)
    return out


def references(cond, qs):
    if cond == "oracle": return orc.oracle_refs(qs)
    rref.set_reference("grok-reasoning"); return rref.references()


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS replicate (qid INTEGER, cond TEXT, vote1 TEXT, vote2 TEXT, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (qid, cond))")
    con.execute("CREATE TABLE IF NOT EXISTS grades (qid INTEGER, cond TEXT, model TEXT, grade REAL, raw TEXT, ts REAL, PRIMARY KEY (qid, cond, model))")
    con.commit(); return con


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rubrics = sj.anchor_rubrics(); anchors = sj.routed_anchor()
    qs, K = ax.questions()
    evals = rj.load_eval_rows(qs, {A, B})
    con = open_cache()
    jobs = []
    for cond in ("grok", "oracle"):
        t = tied(cond); refs = references(cond, sorted(t))
        ql = sorted(t)[:pilot] if pilot else sorted(t)
        done_r = {q for (q,) in con.execute("SELECT qid FROM replicate WHERE cond=?", (cond,))}
        done_g = {(q, m) for q, m in con.execute("SELECT qid, model FROM grades WHERE cond=?", (cond,))}
        for q in ql:
            if q not in refs: continue
            if q not in done_r: jobs.append(("rep", cond, q, refs[q]))
            for m in (A, B):
                if (q, m) not in done_g: jobs.append(("grade", cond, q, refs[q], m))
        print("  %-7s ties %d | replicate to do %d | grades to do %d"
              % (cond, len(t), sum(1 for j in jobs if j[0] == "rep" and j[1] == cond),
                 sum(1 for j in jobs if j[0] == "grade" and j[1] == cond)))
    calls = sum(2 if j[0] == "rep" else 1 for j in jobs)
    print("AGGREGATE: %d jobs (%d calls) | workers %d" % (len(jobs), calls, workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        kind, cond, q, ref = job[0], job[1], job[2], job[3]
        ra, rb, anc = evals.get((q, A)), evals.get((q, B)), anchors.get(q)
        if ra is None or rb is None or anc is None: return None
        sp, rub = rubrics[anc]
        qtext = rref.with_reference(ra[0], ref)
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        if kind == "rep":
            system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
            r1 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, ta, tb))[0])
            r2 = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(qtext, tb, ta))[0])
            v1, _ = rj.parse_judge(r1); v2, _ = rj.parse_judge(r2)
            return ("rep", (q, cond, v1, v2, r1, r2, time.time()))
        m = job[4]
        raw = rr.strip_think(rr.call_judge(pt.SYSTEM % (sp, pt.VERIFY_REF, rub), pt.USER % (qtext, ta if m == A else tb))[0])
        g, _ = pt.parse(raw)
        if g is None: return None
        return ("grade", (q, cond, m, g, raw, time.time()))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: r = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][2], str(e)[:110]), flush=True); continue
            if r is None: skip += 1; continue
            with lock:
                if r[0] == "rep": con.execute("INSERT OR REPLACE INTO replicate VALUES (?,?,?,?,?,?,?)", r[1])
                else: con.execute("INSERT OR REPLACE INTO grades VALUES (?,?,?,?,?,?)", r[1])
                con.commit()
            ok += 1
            if i % 50 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    qs, K = ax.questions()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L = {(q, m): len(o or "") for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results") if m in (A, B)}
    con = open_cache()
    REP = {(q, c): (v1, v2) for q, c, v1, v2 in con.execute("SELECT qid, cond, vote1, vote2 FROM replicate")}
    GR = {(q, c, m): g for q, c, m, g in con.execute("SELECT qid, cond, model, grade FROM grades")}
    out = []
    kw = sum(1 for q in qs if K[(q, A)])
    out.append("=== AGGREGATE: two order-symmetric tie-breaks on the questions the dual-order rule abstained on ===")
    out.append("  population: the %d questions where %s and %s differ | key rate for %s %.3f" % (len(qs), A, B, A, kw / len(qs)))

    for cond, base_acc in (("grok", 0.612), ("oracle", 0.777)):
        src = {q: (v1, v2, w, inv) for q, v1, v2, w, inv in sqlite3.connect("file:%s?mode=ro" % SRC[cond], uri=True).execute(
            "SELECT qid, vote1, vote2_raw, winner, invalid FROM pairwise")}
        judged = [q for q in qs if q in src and not src[q][3]]
        ties = [q for q in judged if src[q][2] == "TIE"]
        base = {q: src[q][2] for q in judged}
        truth = lambda q: A if K[(q, A)] else B

        def rule_replicate(q):
            votes = [canon(src[q][0], 1), canon(src[q][1], 2)]
            r = REP.get((q, cond))
            if r: votes += [canon(r[0], 1), canon(r[1], 2)]
            votes = [v for v in votes if v]
            na, nb = votes.count(A), votes.count(B)
            return A if na > nb else (B if nb > na else "TIE")

        def rule_grade(q):
            ga, gb = GR.get((q, cond, A)), GR.get((q, cond, B))
            if ga is None or gb is None: return "TIE"
            return "TIE" if ga == gb else (A if ga > gb else B)

        out.append("")
        out.append("  ---- reference: %s | %d judged, %d ties (%.1f%%), current accuracy %.3f ----"
                   % ("the DEPLOYED grok reference" if cond == "grok" else "the ORACLE (answer key)",
                      len(judged), len(ties), 100 * len(ties) / len(judged), base_acc))
        out.append("      the key makes %s the winner on %.3f of the TIED questions vs %.3f of the decided ones"
                   % (A, sum(1 for q in ties if K[(q, A)]) / max(1, len(ties)),
                      sum(1 for q in judged if q not in ties and K[(q, A)]) / max(1, len(judged) - len(ties))))
        for name, rule in (("REPLICATE (majority of 4)", rule_replicate), ("GRADE (pointwise tie-break)", rule_grade)):
            resolved = {q: rule(q) for q in ties}
            got = sum(1 for q in ties if resolved[q] != "TIE")
            acc_ties = sum(1 for q in ties if resolved[q] == truth(q)) / max(1, len(ties))
            merged = {q: (resolved[q] if q in ties else base[q]) for q in judged}
            acc_all = sum(1 for q in judged if merged[q] == truth(q)) / len(judged)
            dec = [q for q in judged if merged[q] != "TIE"]
            wa = sum(1 for q in dec if merged[q] == A)
            p = ax.binom_p(wa, len(dec))
            longer = sum(1 for q in ties if resolved[q] != "TIE" and L[(q, resolved[q])] > L[(q, A if resolved[q] == B else B)])
            acc_res = sum(1 for q in ties if resolved[q] != "TIE" and resolved[q] == truth(q)) / max(1, got)
            out.append("      %-28s resolved %2d of %2d ties | accuracy ON THE TIES %.3f (was 0.000 by convention) | overall %.3f (%+.3f)"
                       % (name, got, len(ties), acc_ties, acc_all, acc_all - base_acc))
            out.append("          accuracy on the ones it actually RESOLVES %.3f - the abstentions were not unresolvable, they were unresolved"
                       % acc_res)
            out.append("          %s win rate %.3f (binomial p=%.4f) over %d decided -> order recovered: %s | tie-break winner is the longer answer %d of %d"
                       % (A, wa / max(1, len(dec)), p, len(dec), "YES" if (wa / max(1, len(dec)) > 0.5 and p < 0.05) else "NO", longer, got))
        rem = [q for q in ties if rule_replicate(q) == "TIE"]
        out.append("      ties remaining after REPLICATE: %d | the key makes %s the winner on %.3f of them"
                   % (len(rem), A, sum(1 for q in rem if K[(q, A)]) / max(1, len(rem))))
    txt = "\n".join(out)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze()
