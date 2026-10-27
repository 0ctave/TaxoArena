"""J1-R readout: grok-4-1-fast-reasoning WITH the J2-R reference vs the same judge WITHOUT it (J1 cache), paired."""
import os, sys, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rejudge_grok as rj
import rubric_p8 as p8
import judge_free_tests as jf

D = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "experiment_results", "x12_crossdomain")
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]


def load(name):
    c = sqlite3.connect("file:%s?mode=ro" % os.path.join(D, name), uri=True)
    return {r[0]: r for r in c.execute("SELECT match_id, model_a, model_b, qid, r1_winner, r1_flip, r1_invalid FROM verdicts")}


ref = load("rejudge_grok_4_1_fast_reasoning_refgrok.db")
base = load("rejudge_grok_4_1_fast_reasoning.db")
ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
rows = {}
for mid, r in ref.items():
    b = base.get(mid)
    if r[6] or b is None or b[6]: continue
    _, a, bb, q, w, fl, _ = r
    ca, cb = G.get((q, a)), G.get((q, bb))
    if ca is None or cb is None or ca == cb: continue
    d = a if ca else bb
    rows[mid] = dict(ref=(w == d), base=(b[4] == d), top=(a in TOP4 and bb in TOP4), tie=(w == "TIE"), flip=fl)
keys = list(rows)
n_inv = sum(1 for r in ref.values() if r[6])
print("=== J1-R: grok-4-1-fast-reasoning + reasoning reference vs the same judge without it (J1), %d judged (%d invalid), %d key-decidable paired ===" % (len(ref), n_inv, len(keys)))
for lab, ks in (("ALL", keys), ("TOP-CLUSTER", [k for k in keys if rows[k]["top"]])):
    n = len(ks); pr = sum(rows[k]["ref"] for k in ks) / n; pb = sum(rows[k]["base"] for k in ks) / n
    b = sum(rows[k]["ref"] and not rows[k]["base"] for k in ks); c = sum(rows[k]["base"] and not rows[k]["ref"] for k in ks)
    print("  %-12s n=%4d | with ref %.3f vs without %.3f (%+.3f) | %d:%d | p=%.4f" % (lab, n, pr, pb, pr - pb, b, c, p8.mcn(b, c)))
    if lab == "ALL":
        print("  REGISTERED (gain > 0 at p < 0.05): %s" % ("PASS" if (pr > pb and p8.mcn(b, c) < 0.05) else "FAIL"))
        print("  DESCRIPTIVE: STACK-v2 (Mistral) 0.865 vs this ceiling %.3f -> gap %+.3f; decidable ties %.3f; flip rate %.3f" % (pr, 0.865 - pr, sum(rows[k]["tie"] for k in keys) / len(keys), sum(rows[k]["flip"] for k in keys) / len(keys)))
acc, _ = jf.gt_and_lengths(set(TOP4)); gt = sorted(TOP4, key=lambda m: -acc[m])
for name, src in (("without ref (J1)", base), ("with ref (J1-R)", ref)):
    top = [r for r in src.values() if not r[6] and r[1] in TOP4 and r[2] in TOP4]
    th = jf.board_from(((r[1], r[2], 0.5 if r[4] == "TIE" else (1.0 if r[4] == r[1] else 0.0), 1.0) for r in top), TOP4)
    o, pv, _ = jf.violations(th, gt)
    print("  top-4 board [%s]: %s (%d violations; key %s)" % (name, " > ".join(o), pv, " > ".join(gt)))
