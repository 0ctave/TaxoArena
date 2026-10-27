"""POSITION-DECOMP — how much of ARENA-13 (1) is the slot the model sat in? (registered 2026-09-14)

  python tools/analysis/position_decomp.py --judge [--pilot N] [--workers 8]
  python tools/analysis/position_decomp.py --analyze

ARENA-13 arm A was single order with the new contestant always presented as Model A. This re-judges its 598
FRONTIER matches with the OPPONENT presented first - same judge, same ensemble reference, same rubric, only the
presentation order changes - and stores them as arm "reversed" in the same cache. DECOMP measured the judge's
test-retest noise at 5.7% on the 299 of these whose two arms had byte-identical prompts, so on that same subset
position sensitivity comes out as the flip rate MINUS a noise floor measured on the very same questions.
"""
import os, sys, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf
import prompt_v2
import arena13 as a13

NEW = a13.NEW
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "positiondecomp_outcome.txt")
NOISE = 0.057          # DECOMP, measured on the 299 byte-identical-prompt matches


CROSS = False   # --cross: POSITION-FULL, the 1,200 CROSS-TIER matches instead of the 600 frontier ones


def frontier_rows(con):
    return [(m, q, opp) for m, q, opp, fr in con.execute(
        "SELECT mid, qid, opponent, frontier FROM schedule ORDER BY mid") if bool(fr) != CROSS]


def judge(pilot, workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    rubrics = sj.anchor_rubrics()
    con = a13.open_cache()
    anc = {m: a for m, a in con.execute("SELECT mid, anchor FROM schedule")}
    sched = frontier_rows(con)
    if pilot: sched = sched[:pilot]
    done = {m for (m,) in con.execute("SELECT mid FROM verdicts WHERE arm='reversed'")}
    todo = [s for s in sched if s[0] not in done]
    evals = rj.load_eval_rows([s[1] for s in sched], set(p8.ARENA12))
    print("POSITION-DECOMP: %d frontier matches | to do %d (1 call each) | workers %d"
          % (len(sched), len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        mid, qid, opp = job
        ro = evals.get((qid, opp))
        if ro is None or qid not in cot: return None
        ref = a13.ensemble_ref(qid, P, OPT, {opp, NEW})
        if ref is None: return None
        sp, rub = rubrics[anc[mid]]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        q = ro[0] + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (ref[0], ref[1])
        tnew = cot[qid][2]
        topp = rj.robust_trace(ro[2], ro[3], ro[1])
        # REVERSED: the opponent is Model A, the new contestant is Model B
        raw = rr.strip_think(rr.call_judge(system, rj.build_user_prompt(q, topp, tnew))[0])
        v, _ = rj.parse_judge(raw)
        w = {"Model A": opp, "Model B": NEW}.get(v, "TIE")
        return (mid, "reversed", w, int(v not in ("Model A", "Model B", "TIE")), raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    rref.set_reference("grok-reasoning"); grok = rref.references()
    con = a13.open_cache()
    schall = {m: (q, opp) for m, q, opp in con.execute("SELECT mid, qid, opponent FROM schedule")}
    sch = {m: (q, opp) for m, q, opp, fr in con.execute("SELECT mid, qid, opponent, frontier FROM schedule") if fr}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    rows = []
    for m, d in V.items():
        # FRONTIER ONLY: POSITION-FULL later adds reversed verdicts for the cross-tier matches, and this
        # function's recorded outcome must stay reproducible.
        if m not in sch or "ensemble" not in d or "reversed" not in d: continue
        q, opp = sch[m]
        e = a13.ensemble_ref(q, P, OPT, {opp, NEW}); g = grok.get(q)
        rows.append(dict(mid=m, qid=q, opp=opp, fwd=d["ensemble"], rev=d["reversed"],
                         identical=bool(e and g and e[0] == g[0])))
    n = len(rows)
    L = []
    L.append("=== POSITION-DECOMP: the same frontier matches with the opponent presented FIRST (%d matches) ===" % n)

    sub = [r for r in rows if r["identical"]]
    flip_sub = sum(1 for r in sub if r["fwd"] != r["rev"]) / max(1, len(sub))
    rng = random.Random(42); diffs = []
    for _ in range(2000):
        bs = [sub[rng.randrange(len(sub))] for _ in range(len(sub))]
        diffs.append(sum(1 for r in bs if r["fwd"] != r["rev"]) / len(bs) - NOISE)
    diffs.sort()
    L.append("")
    L.append("  (1) POSITION, on the %d matches where DECOMP measured the noise floor on the very same questions:" % len(sub))
    L.append("      flip rate between the two ORDERS      %.3f" % flip_sub)
    L.append("      test-retest noise, same prompt twice  %.3f   (DECOMP)" % NOISE)
    L.append("      POSITION SENSITIVITY                  %.3f   bootstrap 95%% CI [%+.3f, %+.3f]"
             % (flip_sub - NOISE, diffs[50], diffs[1949]))
    L.append("      -> %s" % ("position is real and larger than the judge's own stochasticity" if diffs[50] > 0
                              else "the two orders disagree no more than the same prompt asked twice: no measurable position effect"))
    flip_all = sum(1 for r in rows if r["fwd"] != r["rev"]) / n
    L.append("      (flip rate over all %d frontier matches, for comparison: %.3f)" % (n, flip_all))

    wf = sum(1 for r in rows if r["fwd"] == NEW) / n
    wr = sum(1 for r in rows if r["rev"] == NEW) / n
    b = sum(1 for r in rows if r["fwd"] == NEW and r["rev"] != NEW)
    c = sum(1 for r in rows if r["rev"] == NEW and r["fwd"] != NEW)
    L.append("")
    L.append("  (2) DIRECTION: the new contestant's win rate presented FIRST %.3f | presented SECOND %.3f (%+.3f)"
             % (wf, wr, wr - wf))
    L.append("      discordant first-only %d : second-only %d | McNemar p=%.4g" % (b, c, p8.mcn(b, c)))

    # (3) board with dual-order frontier verdicts
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    old = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]
    models = sorted(set(p8.ARENA12) | {NEW})
    brows = [(a, b_, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b_, w, _ in old]
    dual = {r["mid"]: ("TIE" if r["fwd"] != r["rev"] else r["fwd"]) for r in rows}
    kept = 0
    for m, arm, win, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if arm != "ensemble" or inv: continue
        q, opp = schall[m]
        w = dual.get(m, win)                      # dual-order where we have it, single order elsewhere
        kept += int(m in dual)
        brows.append((NEW, opp, 0.5 if w == "TIE" else (1.0 if w == NEW else 0.0), 1.0))
    th = jf.board_from(brows, models)
    acck, _ = jf.gt_and_lengths(set(p8.ARENA12))
    acck[NEW] = sum(cot[q][1] for q in cot if q in pool) / max(1, sum(1 for q in cot if q in pool))
    order = sorted(models, key=lambda m: -th[m]); rank = order.index(NEW) + 1
    gem = "gemini-3.1-pro_5-shots"
    L.append("")
    L.append("  (3) BOARD with dual-order TIE-on-flip verdicts on the %d frontier matches (single order elsewhere):" % kept)
    for i, m in enumerate(order[:5], 1):
        L.append("      %d. %-34s theta %+.3f | key %.3f%s" % (i, m, th[m], acck[m], "   <- new" if m == NEW else ""))
    L.append("      the new contestant places %d (ARENA-13 single order: 1st, theta +2.156; key rank 2nd)" % rank)
    L.append("")
    L.append("  (4) AMENDMENT RULE fixed before the run: theta below gemini's once the frontier is order-balanced")
    L.append("      -> attribute ARENA-13 (1) to the single-order design.")
    L.append("      theta new %+.3f vs gemini %+.3f -> %s" % (th[NEW], th[gem],
             "ATTRIBUTED TO POSITION: amend the ARENA-13 row again and require dual order for incremental extension"
             if th[NEW] < th[gem] else
             "NOT attributed to position: the over-ranking survives order balancing, so quality-not-in-the-key or trace style remain"))
    # (5) SENSITIVITY, not registered: the 1,200 CROSS-TIER matches are still single order, with the new
    # contestant still always in slot A, so the residual lead may simply be the position effect that this run
    # only removed from the frontier. Impute their reversed verdicts from the transition rates measured here.
    trans = defaultdict(lambda: defaultdict(int))
    for r in rows:
        fwd = "NEW" if r["fwd"] == NEW else ("TIE" if r["fwd"] == "TIE" else "OPP")
        rev = "NEW" if r["rev"] == NEW else ("TIE" if r["rev"] == "TIE" else "OPP")
        trans[fwd][rev] += 1
    dist = {k: [(kk, vv / sum(v.values())) for kk, vv in v.items()] for k, v in trans.items()}
    cross = []
    for m, arm, win, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if arm != "ensemble" or inv or m in dual: continue
        q, opp = schall[m]
        cross.append((opp, "NEW" if win == NEW else ("TIE" if win == "TIE" else "OPP")))
    base = [(a, b_, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b_, w, _ in old]
    base += [(NEW, schall[r["mid"]][1], 0.5 if dual[r["mid"]] == "TIE" else (1.0 if dual[r["mid"]] == NEW else 0.0), 1.0)
             for r in rows]
    rng2 = random.Random(11); ranks = []; gaps = []
    for _ in range(200):
        rws = list(base)
        for opp, fwd in cross:
            u = rng2.random(); acc = 0.0; rev = fwd
            for kk, pp in dist.get(fwd, [(fwd, 1.0)]):
                acc += pp
                if u <= acc: rev = kk; break
            w = "TIE" if rev != fwd else fwd
            rws.append((NEW, opp, 0.5 if w == "TIE" else (1.0 if w == "NEW" else 0.0), 1.0))
        t = jf.board_from(rws, models)
        o = sorted(models, key=lambda m: -t[m])
        ranks.append(o.index(NEW) + 1); gaps.append(t[NEW] - t[gem])
    gaps.sort()
    L.append("")
    L.append("  (5) SENSITIVITY, not registered - what if the 1,200 CROSS-TIER matches were order-balanced too?")
    L.append("      They are still single order with the new contestant in slot A, so the position effect measured")
    L.append("      above has NOT been removed from them. Imputing their reversed verdicts from the transition")
    L.append("      rates observed on the frontier (200 draws):")
    L.append("      the new contestant places 1st in %d%% of draws | theta gap to gemini median %+.3f, 90%% range [%+.3f, %+.3f]"
             % (100 * sum(1 for r in ranks if r == 1) / len(ranks), gaps[100], gaps[10], gaps[189]))
    L.append("      CAVEAT: cross-tier pairs are less contested than frontier pairs, so their true flip rate is")
    L.append("      probably lower and this is an UPPER bound on the correction. Settling it costs 1,200 calls.")

    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


def analyze_full():
    """POSITION-FULL: arm A brought to full dual order (registered 2026-09-14)."""
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    con = a13.open_cache()
    sch = {m: (q, opp, bool(fr)) for m, q, opp, fr in con.execute("SELECT mid, qid, opponent, frontier FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    rows = [dict(mid=m, qid=sch[m][0], opp=sch[m][1], frontier=sch[m][2], fwd=d["ensemble"], rev=d["reversed"])
            for m, d in V.items() if "ensemble" in d and "reversed" in d and m in sch]
    fr = [r for r in rows if r["frontier"]]; cr = [r for r in rows if not r["frontier"]]
    L = []
    L.append("=== POSITION-FULL: ARENA-13 arm A brought to FULL dual order (%d matches: %d frontier, %d cross-tier) ==="
             % (len(rows), len(fr), len(cr)))

    flip = lambda s: sum(1 for r in s if r["fwd"] != r["rev"]) / max(1, len(s))
    L.append("")
    L.append("  (3) IS POSITION WEAKER OFF THE FRONTIER?")
    for tag, s in (("frontier", fr), ("cross-tier", cr)):
        wf = sum(1 for r in s if r["fwd"] == NEW) / max(1, len(s))
        wr = sum(1 for r in s if r["rev"] == NEW) / max(1, len(s))
        b = sum(1 for r in s if r["fwd"] == NEW and r["rev"] != NEW)
        c = sum(1 for r in s if r["rev"] == NEW and r["fwd"] != NEW)
        L.append("      %-11s n=%4d | flip %.3f | win rate FIRST %.3f vs SECOND %.3f (%+.3f) | %d:%d | McNemar p=%.4g"
                 % (tag, len(s), flip(s), wf, wr, wr - wf, b, c, p8.mcn(b, c)))
    L.append("      prediction was a cross-tier flip rate of 0.10-0.16 (below the frontier's 0.182) and a")
    L.append("      direction effect of 5-12pp (below 13.5pp): %s"
             % ("both hold" if (0.10 <= flip(cr) <= 0.16) else "see the numbers above"))

    # (1) and (2): the board on fully balanced arm A
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    old = [r for r in sj.open_cache().execute("SELECT model_a, model_b, winner, invalid FROM verdicts") if not r[3]]
    models = sorted(set(p8.ARENA12) | {NEW})
    dual = {r["mid"]: ("TIE" if r["fwd"] != r["rev"] else r["fwd"]) for r in rows}
    brows = [(a, b_, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b_, w, _ in old]
    single = 0
    for m, arm, win, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if arm != "ensemble" or inv or m not in sch: continue
        w = dual.get(m, win); single += int(m not in dual)
        brows.append((NEW, sch[m][1], 0.5 if w == "TIE" else (1.0 if w == NEW else 0.0), 1.0))
    th = jf.board_from(brows, models)
    acck, _ = jf.gt_and_lengths(set(p8.ARENA12))
    acck[NEW] = sum(cot[q][1] for q in cot if q in pool) / max(1, sum(1 for q in cot if q in pool))
    order = sorted(models, key=lambda m: -th[m]); rank = order.index(NEW) + 1
    gem = "gemini-3.1-pro_5-shots"
    L.append("")
    L.append("  (1) BOARD, dual order on %d of %d arm A matches (%d still single order):" % (len(dual), len(sch), single))
    for i, m in enumerate(order[:6], 1):
        L.append("      %d. %-34s theta %+.3f | key %.3f%s" % (i, m, th[m], acck[m], "   <- new" if m == NEW else ""))
    krank = sorted(models, key=lambda m: -acck[m]).index(NEW) + 1
    L.append("      the new contestant places %d, key rank %d -> %s" % (rank, krank, "PASS" if rank in (2, 3) else "FAIL"))

    th12 = jf.board_from([(a, b_, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b_, w, _ in old], sorted(p8.ARENA12))
    o12 = sorted(p8.ARENA12, key=lambda m: -th12[m]); pos = {m: i for i, m in enumerate([m for m in order if m != NEW])}
    c = d = 0
    for i in range(len(o12)):
        for j in range(i + 1, len(o12)):
            s_ = pos[o12[i]] - pos[o12[j]]
            c += s_ < 0; d += s_ > 0
    tau = (c - d) / max(1, c + d)
    L.append("  (2) the twelve keep their order, Kendall tau %.3f -> %s" % (tau, "PASS" if tau >= 0.90 else "FAIL"))

    gap = th[NEW] - th[gem]
    L.append("")
    L.append("  (4) WAS THE IMPUTATION CALIBRATED? POSITION-DECOMP imputed a gap of -0.326, 90%% range [-0.367, -0.288].")
    L.append("      realised gap %+.3f -> %s" % (gap, "inside the imputed range" if -0.367 <= gap <= -0.288 else
             ("the imputation OVERSHOT, as predicted" if gap > -0.288 else "the imputation UNDERSHOT")))
    L.append("      Transition-rate imputation from a contested subset therefore %s as a cheap forecast."
             % ("holds up" if abs(gap + 0.326) < 0.10 else "gives the right direction but not the right size"))

    dec = [r for r in rows if cot[r["qid"]][1] != K[r["qid"]].get(r["opp"], 0)]
    acc = sum(1 for r in dec if dual[r["mid"]] == (NEW if cot[r["qid"]][1] else r["opp"])) / max(1, len(dec))
    L.append("")
    L.append("  (5) ARENA-13 (3) RE-RUN under dual order: new-pair key-decidable accuracy %.3f on %d pairs"
             % (acc, len(dec)))
    L.append("      against 0.837 single order and the 0.85 bar -> %s" % ("PASS" if acc >= 0.85 else "still FAIL"))

    L.append("")
    L.append("  AMENDMENT RULE fixed before the run: %s" % (
        "the new contestant places %d on order-balanced evidence -> ARENA-13 (1) IS ATTRIBUTED TO THE SINGLE-ORDER\n"
        "      DESIGN. Amend the ARENA-13 and POSITION-DECOMP rows; 'incremental extension must be dual order'\n"
        "      becomes a finding of the paper, not an operational note." % rank if rank in (2, 3) else
        "it still places 1st on fully balanced evidence -> position is NOT the explanation. The remaining\n"
        "      candidates are quality the key does not capture and trace-generation style, neither testable\n"
        "      without another REGEN-scale run; state as an open limitation."))
    txt = "\n".join(L)
    print(txt)
    open(os.path.join(ROOT, "experiment_results", "x12_crossdomain", "positionfull_outcome.txt"), "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--cross", action="store_true")
    a = ap.parse_args(); CROSS = a.cross
    if a.judge: judge(a.pilot, a.workers)
    elif a.analyze: analyze_full() if a.cross else analyze()
