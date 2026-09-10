"""RUBRIC KIT v2 — the data-only leaf card (RK-1b) and reasoning-backed worked neighbours (RK-1c).
(docs/rubric_v2_design.md "What the data can tell a judge about a leaf"; registered before any judged call.)

  --datacard          zero LLM calls: per leaf of bareq512_s42, from TRAIN-side questions only —
                      answer form (numeric share, option spacing), numeric error signature (near-miss,
                      ×2/÷2, ×10/÷10 shares among the 46 models' wrong picks) and the top attractor
                      pairs (correct option text vs the dominant distractor, with prevalence). Attractor
                      pairs whose correct text equals any judged question's correct option (exact,
                      case-insensitive) are dropped; the 5-gram leakage audit runs at judge time.
  --solve-neighbours  grok-reasoning solves every distinct TRAIN-side neighbour of the R3 questions
                      (K3 material) with its reasoning kept; only KEY-VERIFIED solves are used as worked
                      examples (~2k calls). Never an arena question.
  --judge --variant datacard   RK-1b: STACK-v2 vs STACK-v2 + data card (both fresh, interleaved)
  --judge --variant reasoned   RK-1c: STACK-v2 vs STACK-v2 + data card + reasoning-backed neighbours
  --analyze --variant ...

REGISTERED (both): +1pp at paired McNemar p < 0.05 on key-decidable; secondary quantitative > discursive.
Predictions: RK-1b +0 to +2pp (the card is short and checkable; the near-miss/factor-2 warnings are the
first leaf-specific content ever handed to the judge); RK-1c +1 to +3pp (worked solutions are the
strongest verifiable material short of the key itself).
"""
import os, sys, re, json, time, math, random, sqlite3, argparse, threading, urllib.error
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import rubric_512 as r512
import stack_judge as sj
import rubric_kit as rk
import leaf_guideline_signals as lgs
import prompt_v2

KIT_DB = rk.KIT_DB
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_kit2.db")
QUANT = rk.QUANT
SOLVE_SYSTEM = ("You are an expert solver. Solve the multiple-choice question step by step, showing the reasoning and the key formulas "
                "or facts used, then end with a line 'Final answer: (X)' giving the option letter.")


def open_kit():
    con = rk.open_kit()
    con.execute("CREATE TABLE IF NOT EXISTS datacard (leaf TEXT PRIMARY KEY, label TEXT, anchor TEXT, text TEXT, n_train INTEGER, ts REAL)")
    con.execute("CREATE TABLE IF NOT EXISTS solves (qtext TEXT PRIMARY KEY, answer TEXT, correct INTEGER, reasoning TEXT, tokens INTEGER, ts REAL)")
    con.commit()
    return con


def datacard():
    models, G, qs, leaf, anc = lgs.lpe.assign_leaves()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    meta = {}
    for q, o, a, r, t in ev.execute("SELECT question_id, options_json, gt_answer, is_reserved, question_text FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        try: meta[q] = (json.loads(o) if o else [], (a or "").strip().upper()[:1], bool(r), t)
        except Exception: pass
    preds = defaultdict(Counter)
    for q, m, p in ev.execute("SELECT question_id, model_name, pred FROM eval_results WHERE model_name != 'Meta-Llama-3-70B-Instruct'"):
        if q in meta and p and p[:1] != meta[q][1]: preds[q][p[:1]] += 1
    sample = rj.sample_matches(); judged = {int(m[1]) for m in sample}
    judged_correct = {meta[q][0]["ABCDEFGHIJ".find(meta[q][1])].strip().lower() for q in judged if q in meta and 0 <= "ABCDEFGHIJ".find(meta[q][1]) < len(meta[q][0])}
    # The judge-time audit refuses any 5-gram shared with a judged question's correct option (formulaic
    # phrases such as "it's not the case that" included); apply the same rule when selecting pairs.
    judged_grams = set()
    for t in judged_correct:
        if len(t.split()) >= 5: judged_grams |= rk.grams(t)
    def shares(t): return bool(rk.grams(t) & judged_grams)
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42")); labels = {n["id"]: n["label"] for n in nodes.values()}
    by_leaf = defaultdict(list)
    for q in qs:
        if q in meta and not meta[q][2]: by_leaf[leaf[q]].append(q)     # TRAIN side only
    con = open_kit(); n_cards = 0
    for l, lq in by_leaf.items():
        numeric = 0; spacing = []; ratios = Counter(); pairs = []
        for q in lq:
            opts, key, _, _ = meta[q]; ki = "ABCDEFGHIJ".find(key)
            if ki < 0 or ki >= len(opts): continue
            vals = [lgs.parse_num(o) for o in opts]; kv = vals[ki]
            wrong = preds.get(q, Counter()); nw = sum(wrong.values())
            if kv is not None and sum(v is not None for v in vals) >= 0.7 * len(vals):
                numeric += 1
                others = [abs(v / kv) for v in vals if v is not None and v != kv and kv != 0 and v != 0]
                if others: spacing.append(min(abs(math.log10(x)) for x in others))
                for p, k in wrong.items():
                    pi = "ABCDEFGHIJ".find(p); v = vals[pi] if 0 <= pi < len(vals) else None
                    if v is None or kv == 0 or v == 0: continue
                    r = v / kv
                    tag = ("sign" if r < 0 else "x2/÷2" if min(abs(math.log2(abs(r)) - 1), abs(math.log2(abs(r)) + 1)) < 0.12 else
                           "x10/÷10" if min(abs(math.log10(abs(r)) - 1), abs(math.log10(abs(r)) + 1)) < 0.05 else "near-miss(<10%)" if abs(math.log10(abs(r))) < 0.041 else "other")
                    ratios[tag] += k
            if nw >= 8:
                p, k = wrong.most_common(1)[0]; pi = "ABCDEFGHIJ".find(p)
                # Only CONCEPTUAL pairs transfer to other questions (a numeric pair is question-specific;
                # the aggregate error signature carries the numeric information). Drop empty/nan options.
                if (k / nw >= 0.4 and 0 <= pi < len(opts) and opts[ki].strip().lower() not in judged_correct
                        and vals[ki] is None and vals[pi] is None and opts[ki].strip().lower() not in ("", "nan") and opts[pi].strip().lower() not in ("", "nan")
                        and sum(ch.isdigit() for ch in opts[ki]) < 3 and sum(ch.isdigit() for ch in opts[pi]) < 3   # conceptual text only
                        and not shares(opts[ki]) and not shares(opts[pi])):
                    pairs.append((k / nw, nw, opts[ki].strip(), opts[pi].strip()))
        pairs.sort(key=lambda x: -x[0] * x[1])
        lines = ["Answer form in this subdomain: %d%% of questions have numeric options" % round(100 * numeric / max(1, len(lq)))]
        if spacing: lines.append("Distractor spacing: the nearest wrong value sits within a factor 10^%.2f of the correct one (median) — a near-miss is a wrong answer; carry full precision" % float(np.median(spacing)))
        tot = sum(ratios.values())
        if tot >= 20:
            sig = ", ".join("%s %d%%" % (k, round(100 * v / tot)) for k, v in ratios.most_common(4) if k != "other")
            if sig: lines.append("Numeric error signature (how 46 models go wrong here): %s of wrong numeric picks — check the corresponding step explicitly" % sig)
        if pairs:
            lines.append("Typical misconceptions observed in this subdomain (wrong choice vs correct, from training questions):")
            for share, nw, cor, dis in pairs[:6]:
                lines.append("  - models pick \"%s\" instead of \"%s\" (%d%% of %d wrong picks)" % (dis[:90], cor[:90], round(100 * share), nw))
        text = "\n".join(lines)
        con.execute("INSERT OR REPLACE INTO datacard VALUES (?,?,?,?,?,?)", (l, labels.get(l, l), anc[lq[0]], text, len(lq), time.time())); n_cards += 1
    con.commit()
    print("datacards: %d leaves | example:\n%s" % (n_cards, con.execute("SELECT text FROM datacard WHERE anchor='Physics' ORDER BY n_train DESC LIMIT 1").fetchone()[0]))


def solve_neighbours(workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-reasoning"; rr.load_env()
    con = open_kit()
    mp = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    rows = {r[0]: r for r in mp.execute("SELECT question, options, answer FROM mmlu_pro")}
    need = set()
    for q, payload in con.execute("SELECT qid, payload FROM neighbours"):
        for e in json.loads(payload):
            qt = e["text"].split("\n")[0][3:]          # "Q: ..." first line
            if qt in rows: need.add(qt)
    done = {r[0] for r in con.execute("SELECT qtext FROM solves")}
    todo = sorted(need - done)
    print("neighbour solves: distinct train neighbours %d | done %d | to solve %d | workers %d" % (len(need), len(done), len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = 0

    def one(qt):
        question, options, answer = rows[qt]
        try: opts = json.loads(options) if options and options.strip().startswith("[") else [o.strip() for o in (options or "").split("|")]
        except Exception: opts = [options or ""]
        user = question + "\n\nOptions:\n" + "\n".join("(%s) %s" % ("ABCDEFGHIJ"[i], o) for i, o in enumerate(opts))
        content, _, tokens, _ = rr.call_judge(SOLVE_SYSTEM, user)
        content = rr.strip_think(content)
        m = re.findall(r"Final answer:\s*\(?([A-J])\)?", content)
        a = m[-1] if m else ""
        return (qt, a, int(a == (answer or "")[:1].upper()), content, tokens or 0, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, qt): qt for qt in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR: %s" % str(e)[:100], flush=True); continue
            with lock:
                con.execute("INSERT OR REPLACE INTO solves VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, err %d)" % (i, len(todo), ok, err), flush=True)
    c, n = con.execute("SELECT sum(correct), count(*) FROM solves").fetchone()
    print("done: ok %d, errors %d | verified-correct solves %d of %d" % (ok, err, c or 0, n), flush=True)


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, leaf TEXT, "
                "vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.commit()
    return con


def judge(variant, pilot, workers):
    p8.load_env(); rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics(); route = r512.primary_routing("bareq512_s42"); anchors = sj.routed_anchor()
    kcon = open_kit()
    cards = {l: t for l, t in kcon.execute("SELECT leaf, text FROM datacard")}
    neigh = {q: json.loads(p) for q, p in kcon.execute("SELECT qid, payload FROM neighbours")}
    solves = {qt: (a, r) for qt, a, c, r in kcon.execute("SELECT qtext, answer, correct, reasoning FROM solves WHERE correct=1")}
    kcon.close()
    sample = rj.sample_matches()
    assert rk.leakage_audit({(l, "datacard"): t for l, t in cards.items()}, sample), "data card leaks option text"
    if variant == "reasoned":
        assert len(solves) > 500, "too few verified neighbour solves (%d)" % len(solves)
    if pilot: sample = sample[:pilot]
    cache = open_cache(); done = {(m, a) for m, a in cache.execute("SELECT match_id, arm FROM verdicts")}
    arm_kit = "datacard" if variant == "datacard" else "reasoned"
    todo = [(m, arm) for m in sample for arm in ("stackv2_" + variant, arm_kit) if (m[0], arm) not in done and int(m[1]) in route]
    evals = rj.load_eval_rows([int(m[1]) for m, _ in todo], {m[2] for m, _ in todo} | {m[3] for m, _ in todo})
    print("RK-1%s: sample %d | jobs %d (%d calls) | workers %d | cards %d | verified solves %d" % ("b" if variant == "datacard" else "c", len(sample), len(todo), 2 * len(todo), workers, len(cards), len(solves)), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m, arm):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb, ref, anc, leaf = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid), route.get(qid)
        if ra is None or rb is None or ref is None or anc is None or leaf is None: return None
        sp, rb_ = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rb_)
        q = rref.with_reference(ra[0], ref)
        if arm in ("datacard", "reasoned"):
            if leaf in cards: system += "\n\nSubdomain data card (measured on training questions of this cell):\n" + cards[leaf]
            if arm == "reasoned":
                exs = []
                for e in neigh.get(qid, []):
                    qt = e["text"].split("\n")[0][3:]
                    if qt in solves:
                        exs.append(e["text"].split("\nReference reasoning:")[0] + "\nVerified worked solution: " + solves[qt][1][:1500])
                if exs: q = "[Solved examples from the same subdomain — training problems with verified solutions; the judged question below is different]\n%s\n\n%s" % ("\n---\n".join(exs[:2]), q)
        system += "\n\n" + rj.SCHEMA_INSTRUCTION
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = p8.call(system, rj.build_user_prompt(q, ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(q, tb, ta))
        v1, c1 = rj.parse_judge(raw1); v2, c2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, arm, a, b, qid, anc, leaf, v1, v2, c1, c2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, arm): (m, arm) for m, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 17), row); cache.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze(variant):
    base, arm = "stackv2_" + variant, ("datacard" if variant == "datacard" else "reasoned")
    cache = open_cache(); V = defaultdict(dict)
    for mid, a_, ma, mb, q, anc, w, inv in cache.execute("SELECT match_id, arm, model_a, model_b, qid, anchor, winner, invalid FROM verdicts"):
        if not inv: V[mid][a_] = (w, ma, mb, q, anc)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = {}
    for mid, arms in V.items():
        if base not in arms or arm not in arms: continue
        w, a, b, q, anc = arms[arm]; ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = {"kit": w == d, "base": arms[base][0] == d, "anchor": anc, "top": a in sj.TOP4 and b in sj.TOP4}
    def stats(ks):
        n = len(ks); pk = sum(rows[k]["kit"] for k in ks) / max(1, n); pb = sum(rows[k]["base"] for k in ks) / max(1, n)
        b = sum(rows[k]["kit"] and not rows[k]["base"] for k in ks); c = sum(rows[k]["base"] and not rows[k]["kit"] for k in ks)
        return n, pk, pb, b, c, p8.mcn(b, c)
    keys = list(rows); n, pk, pb, b, c, p = stats(keys)
    print("=== RK-1%s: STACK-v2 + %s vs STACK-v2 (both fresh), Mistral, %d key-decidable paired ===" % ("b" if variant == "datacard" else "c", arm, n))
    print("  ALL           %s %.3f vs base %.3f (%+.3f) | %d:%d | p=%.4f -> PRIMARY %s" % (arm, pk, pb, pk - pb, b, c, p, "PASS" if (pk - pb >= 0.01 and p < 0.05) else "FAIL"))
    n, pk, pb, b, c, p = stats([k for k in keys if rows[k]["top"]]); print("  TOP-CLUSTER   %.3f vs %.3f (%+.3f) | %d:%d | p=%.4f" % (pk, pb, pk - pb, b, c, p))
    gq = stats([k for k in keys if rows[k]["anchor"] in QUANT]); gd = stats([k for k in keys if rows[k]["anchor"] not in QUANT])
    print("  quantitative  n=%4d %.3f vs %.3f (%+.3f) %d:%d p=%.4f" % (gq[0], gq[1], gq[2], gq[1] - gq[2], gq[3], gq[4], gq[5]))
    print("  discursive    n=%4d %.3f vs %.3f (%+.3f) %d:%d p=%.4f" % (gd[0], gd[1], gd[2], gd[1] - gd[2], gd[3], gd[4], gd[5]))
    print("  SECONDARY (quantitative gain > discursive gain): %s" % ("PASS" if (gq[1] - gq[2]) > (gd[1] - gd[2]) else "FAIL"))
    by = defaultdict(list)
    for k in keys: by[rows[k]["anchor"]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a])[1] - stats(by[a])[2])):
        n, pk, pb, b, c, p = stats(by[anc]); print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, pk - pb, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--datacard", action="store_true"); ap.add_argument("--solve-neighbours", action="store_true")
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--variant", choices=["datacard", "reasoned"], default="datacard")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    if a.datacard: datacard()
    elif a.solve_neighbours: solve_neighbours(a.workers)
    elif a.judge: judge(a.variant, a.pilot, a.workers); analyze(a.variant)
    elif a.analyze: analyze(a.variant)
