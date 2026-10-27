"""SELECTIVE-ORDER — pay for the second order only where it can change anything (registered 2026-09-14, ZERO calls)

  python tools/analysis/selective_order.py

POSITION-FULL measured the flip rate at 0.182 on contested frontier matches and 0.055 - below the 0.057
test-retest floor - on cross-tier ones, so dual order buys nothing on pairs whose candidates already agree.
Three policies replayed on the x12 MAIN cache, which stores both per-order votes for all 9,142 matches:
  ALWAYS DUAL     the production rule, 2 calls per match
  ALWAYS SINGLE   order 1 only, 1 call (ORDER-1 recorded this as a FAIL)
  SELECTIVE       single where the two candidates' own extracted answers AGREE, dual where they DISAGREE
"""
import os, sys, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_p8 as p8
import stack_judge as sj
import judge_free_tests as jf

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "selectiveorder_outcome.txt")


def main():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    P = defaultdict(dict); K = defaultdict(dict)
    for q, m, p, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12: P[q][m] = (p or "").strip().upper()[:1]; K[q][m] = int(c or 0)
    sj.PROMPT = "v2"; sj.ALL_X12 = True
    rows = [r for r in sj.open_cache().execute(
        "SELECT model_a, model_b, qid, vote1, vote2_raw, invalid FROM verdicts") if not r[5]]
    acc, _ = jf.gt_and_lengths(set(p8.ARENA12))
    models = sorted(p8.ARENA12)
    gt4 = sorted(sj.TOP4, key=lambda m: -acc[m])

    def disagree(r):
        pa, pb = P.get(r[2], {}).get(r[0]), P.get(r[2], {}).get(r[1])
        return bool(pa and pb and pa != pb)

    def single(r):
        return {"Model A": r[0], "Model B": r[1]}.get(r[3], "INVALID")

    def dual(r):
        w, _, inv = rj.combine_orders(r[3], r[4])
        return "INVALID" if inv else {"Model A": r[0], "Model B": r[1]}.get(w, w)

    policies = [("ALWAYS DUAL", lambda r: dual(r), lambda r: 2),
                ("ALWAYS SINGLE", lambda r: single(r), lambda r: 1),
                ("SELECTIVE", lambda r: dual(r) if disagree(r) else single(r), lambda r: 2 if disagree(r) else 1)]

    L = ["=== SELECTIVE-ORDER: spend the second call only where the candidates disagree (zero calls) ==="]
    L.append("  x12 MAIN, %d valid matches | %d of them (%.1f%%) have candidates whose own answers DISAGREE"
             % (len(rows), sum(1 for r in rows if disagree(r)), 100 * sum(1 for r in rows if disagree(r)) / len(rows)))
    L.append("")
    L.append("  %-14s %6s %8s %8s %10s %8s %9s" % ("policy", "calls", "calls/m", "rho", "top-4 viol", "ties", "dec.acc"))
    ref = {}
    for name, verdict, cost in policies:
        vs = [(r, verdict(r)) for r in rows]
        vs = [(r, w) for r, w in vs if w != "INVALID"]
        calls = sum(cost(r) for r in rows)
        th = jf.board_from([(r[0], r[1], 0.5 if w == "TIE" else (1.0 if w == r[0] else 0.0), 1.0) for r, w in vs], models)
        rho = jf.rho(th, acc, models)
        _, pv, _ = jf.violations({m: th[m] for m in sj.TOP4}, gt4)
        ties = sum(1 for _, w in vs if w == "TIE") / len(vs)
        dec = [(r, w) for r, w in vs if K[r[2]].get(r[0], 0) != K[r[2]].get(r[1], 0)]
        dacc = sum(1 for r, w in dec if w == (r[0] if K[r[2]][r[0]] else r[1])) / max(1, len(dec))
        ref[name] = (rho, pv, calls)
        L.append("  %-14s %6d %8.2f %8.4f %10d %8.3f %9.3f" % (name, calls, calls / len(rows), rho, pv, ties, dacc))

    rho_d, pv_d, c_d = ref["ALWAYS DUAL"]; rho_s, pv_s, c_s = ref["SELECTIVE"]
    ok = abs(rho_s - rho_d) <= 0.005 and pv_s <= pv_d and c_s < c_d
    L.append("")
    L.append("  REGISTERED BAR for SELECTIVE: rho within 0.005 of ALWAYS DUAL, violations no worse, strictly fewer calls")
    L.append("      rho %.4f vs %.4f (delta %+.4f) | violations %d vs %d | calls %d vs %d (%.0f%% saved) -> %s"
             % (rho_s, rho_d, rho_s - rho_d, pv_s, pv_d, c_s, c_d, 100 * (1 - c_s / c_d), "PASS" if ok else "FAIL"))

    # WHY: the two orders disagree most on exactly the matches the policy economises on
    L.append("")
    L.append("  DIAGNOSTIC - flip rate between the two orders, split by whether the candidates' own answers agree:")
    Ln = {(q, m): l for q, m, l in ev.execute("SELECT question_id, model_name, LENGTH(model_output) FROM eval_results") if m in p8.ARENA12}
    for tag, sel in (("candidates DISAGREE", [r for r in rows if disagree(r)]),
                     ("candidates AGREE", [r for r in rows if not disagree(r)])):
        fl = sum(1 for r in sel if rj.combine_orders(r[3], r[4])[1]) / max(1, len(sel))
        d = [r for r in sel if K[r[2]].get(r[0], 0) != K[r[2]].get(r[1], 0)]
        inv = [(r, single(r)) for r in sel if single(r) not in ("INVALID", "TIE")]
        lng = sum(1 for r, w in inv if Ln.get((r[2], w), 0) > Ln.get((r[2], r[0] if w == r[1] else r[1]), 0)) / max(1, len(inv))
        L.append("      %-20s n=%5d | FLIP RATE %.3f | key-decidable %.3f | single order names a winner on %.3f, the LONGER answer %.0f%% of the time"
                 % (tag, len(sel), fl, len(d) / max(1, len(sel)), len(inv) / max(1, len(sel)), 100 * lng))
    L.append("      READING: the policy was built on the assumption that answer-agreeing pairs are where the second")
    L.append("      call is wasted. They are where it is most NEEDED. Those pairs are almost never key-decidable, so")
    L.append("      there is no right answer for a single order to find - it invents one, with a length preference,")
    L.append("      and only the dual rule's abstention suppresses it. POSITION-FULL's cross-tier finding does not")
    L.append("      transfer: cross-tier pairs mostly DISAGREE on their answers, so 'cross-tier' and 'answer-agreeing'")
    L.append("      are different cuts and I conflated them when designing this policy.")

    # the frontier subset, where the saving is largest and the risk is highest
    top = [r for r in rows if r[0] in sj.TOP4 and r[1] in sj.TOP4]
    nd = sum(1 for r in top if disagree(r))
    L.append("")
    L.append("  TOP-4 PAIRS ONLY (%d matches, %.1f%% disagreeing - the regime the frontier line cares about):"
             % (len(top), 100 * nd / max(1, len(top))))
    for name, verdict, cost in policies:
        vs = [(r, verdict(r)) for r in top]
        vs = [(r, w) for r, w in vs if w != "INVALID"]
        th = jf.board_from([(r[0], r[1], 0.5 if w == "TIE" else (1.0 if w == r[0] else 0.0), 1.0) for r, w in vs], sorted(sj.TOP4))
        o, pv, _ = jf.violations(th, gt4)
        dec = [(r, w) for r, w in vs if K[r[2]].get(r[0], 0) != K[r[2]].get(r[1], 0)]
        dacc = sum(1 for r, w in dec if w == (r[0] if K[r[2]][r[0]] else r[1])) / max(1, len(dec))
        L.append("      %-14s calls %5d (%.2f/match) | %s | %d violations | decidable accuracy %.3f"
                 % (name, sum(cost(r) for r in top), sum(cost(r) for r in top) / len(top),
                    " > ".join(m[:12] for m in o), pv, dacc))
    L.append("")
    L.append("  SCOPE, as registered: this is the matchFilter signal used a second way and the two do not multiply.")
    L.append("  An arena that can DROP answer-agreeing matches should drop them - a six-fold saving on frontier")
    L.append("  pairs. Selective dual order is for arenas that must judge every pair they schedule.")
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
