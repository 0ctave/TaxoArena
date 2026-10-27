"""ARENA-V2 descriptive boards (BOARD-W reporting rule: ungated + confidence-weighted alongside)."""
import os, sys, sqlite3
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rejudge_grok as rj
import judge_free_tests as jf
import stack_judge as sj

sj.PROMPT = "v2"; sj.ALL_X12 = True
TOP4 = sj.TOP4
st = {r[0]: r for r in sj.open_cache().execute("SELECT match_id, model_a, model_b, qid, winner, conf1, conf2, invalid FROM verdicts")}
x12 = {r[0]: r for r in sj.all_x12_matches()}
ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
models = sorted({r[2] for r in x12.values()} | {r[3] for r in x12.values()})
acc, _ = jf.gt_and_lengths(set(models)); gt_order = sorted(TOP4, key=lambda m: -acc[m])


def vote(w, a, b):
    return 0.5 if w == "TIE" else (1.0 if w == a else 0.0)


valid = [r for r in st.values() if not r[7]]
print("12-model board (all %d verdicts) vs key accuracy on the pool:" % len(valid))
th = jf.board_from(((r[1], r[2], vote(r[4], r[1], r[2]), 1.0) for r in valid), models)
for m in sorted(models, key=lambda m: -th[m]):
    print("  %-28s theta %+.3f | key acc %.3f" % (m, th[m], acc[m]))
print("  rho %.4f" % jf.rho(th, acc, models))
top = [r for r in valid if r[1] in TOP4 and r[2] in TOP4]
print("\ntop-4 on the %d top-cluster matches (key order %s):" % (len(top), " > ".join(gt_order)))
for name, rows in (("ungated", ((r[1], r[2], vote(r[4], r[1], r[2]), 1.0) for r in top)),
                   ("mean-confidence-weighted", ((r[1], r[2], vote(r[4], r[1], r[2]) * ((r[5] or 0) + (r[6] or 0)) / 2, ((r[5] or 0) + (r[6] or 0)) / 2) for r in top)),
                   ("gated >= 0.95 both orders", ((r[1], r[2], vote(r[4], r[1], r[2]), 1.0) for r in top if (r[5] or 0) >= 0.95 and (r[6] or 0) >= 0.95))):
    rows = list(rows); t = jf.board_from(rows, TOP4); o, pv, _ = jf.violations(t, gt_order)
    print("  %-26s n=%4d: %s (%d violations)" % (name, len(rows), " > ".join(o), pv))
v1top = [x12[r[0]] for r in top]
t1 = jf.board_from(((r[2], r[3], 0.5 if r[6] else (1.0 if {"Model A": r[2], "Model B": r[3]}.get(r[5], r[5]) == r[2] else 0.0), 1.0) for r in v1top), TOP4)
o, pv, _ = jf.violations(t1, gt_order); print("  %-26s n=%4d: %s (%d violations)" % ("x12 v1 on the same matches", len(v1top), " > ".join(o), pv))
print("\nhead-to-head among the top-4 (STACK-v2 verdicts; key-decidable accuracy of the judge on that pair):")
for i, a in enumerate(TOP4):
    for b in TOP4[i + 1:]:
        pr = [r for r in top if {r[1], r[2]} == {a, b}]
        wa = sum(vote(r[4], a, r[2] if r[1] == a else r[1]) for r in pr)
        dec = [r for r in pr if G.get((r[3], a)) is not None and G.get((r[3], b)) is not None and G[(r[3], a)] != G[(r[3], b)]]
        ok = sum(r[4] == (a if G[(r[3], a)] else b) for r in dec)
        ka = sum(1 for r in dec if G[(r[3], a)]); print("  %-24s vs %-24s n=%3d | %s wins %.2f | key: %s right on %d/%d decidable | judge right %d/%d" % (a, b, len(pr), a[:10], wa / max(1, len(pr)), a[:10], ka, len(dec), ok, len(dec)))
