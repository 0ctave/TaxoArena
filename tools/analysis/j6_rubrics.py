"""J6 — are the rubrics just not good enough? Frontier-induced and CONTRASTIVE anchor rubrics
(docs/judge_improvement_proposals.md "J6"; launch record in docs/judge_v2_program.md; registered before any call).

Induction (grok-4-1-fast-reasoning, ~100 calls): the ladder's induction pipeline (same Kotlin templates,
same anchor corpora = train-side questions with options, key and reference reasoning, pool of record
withheld) with two changes tested separately:
  frontier_anchor     — same corpus, induction model = the reasoning model instead of Mistral;
  contrastive_anchor  — the corpus additionally carries, per anchor, 25 WRONG train-side answers by
                        frontier contestants (key-labelled, truncated), and the instruction asks for
                        rules that DISCRIMINATE those errors from the correct reasoning.
Judging (Mistral-Large-3, R3's 1,980 matches, v1 template, NO reference, dual order, one session,
arms interleaved per match): mistral_anchor (the ladder's Mistral-induced anchor rubric, judged fresh),
frontier_anchor, contrastive_anchor. Comparator for the rubric-vs-nothing question: the same-session
GENERIC verdicts of RUBRIC-512-SS (23:35 session, disclosed as a different session).
REGISTERED: PRIMARY contrastive_anchor > mistral_anchor by paired McNemar p < 0.05 on key-decidable
matches; SECONDARY frontier_anchor > mistral_anchor, same test; leakage audit (shared n-gram >= 5 with
any correct option of a judged question) must be clean for both new rubric sets. Prediction: both null
(+0 to +1pp) — after four clean nulls the prior is that rubric TEXT is not the lever for a judge that
cannot verify; a contrastive gain > +2pp would overturn that and reopen induction as a design axis.

  python tools/analysis/j6_rubrics.py --induce            # ~100 grok-reasoning calls
  python tools/analysis/j6_rubrics.py [--pilot N] [--workers N]   # ~12k Mistral calls
  python tools/analysis/j6_rubrics.py --analyze
"""
import os, sys, re, json, time, random, sqlite3, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rejudge_reasoning as rr
import rubric_ladder as rl
import rubric_p8 as p8
import rubric_512 as r512

DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_j6.db")
LADDER = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_ladder.db")
GENERIC_SS = os.path.join(ROOT, "experiment_results", "rubric_512", "generic_ss.db")
FRONTIER6 = ["gpt-4o-2024-08-06", "gemini-3.1-pro_5-shots", "iask_pro", "arx_0314", "deepseek-chat-v2_5", "Qwen1.5-72B-Chat"]
N_WRONG = 25
ARMS = ("mistral_anchor", "frontier_anchor", "contrastive_anchor")
CONTRAST_INSTRUCTION = """

ADDITIONAL EVIDENCE — WRONG ANSWERS OBSERVED IN THIS DOMAIN (each is a real model response that chose the
wrong option; the correct option is given). Derive from them rules that DISCRIMINATE this domain's typical
failure modes from correct reasoning: what shortcut, misapplied principle, unit/sign/scope error, misread
constraint or unjustified assumption produced each wrong answer, and what a response must show to be
trusted instead. Fold these discriminating rules into the guidelines above.
---
$wrong"""


def open_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS rubrics (kind TEXT, unit TEXT, label TEXT, system_prompt TEXT, rubric TEXT, raw TEXT, ts REAL, PRIMARY KEY (kind, unit))")
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, "
                "vote1 TEXT, vote2_raw TEXT, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.commit()
    return con


def wrong_answers(items):
    """anchor label -> list of (question, chosen, correct, snippet) from TRAIN-side wrong answers (is_reserved=0)."""
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = defaultdict(list)
    marks = ",".join("?" * len(FRONTIER6))
    for cat, qtext, pred, ans, outp in ev.execute(
            "SELECT category, question_text, predicted_answer, correct_answer, model_output FROM eval_results "
            "WHERE is_reserved=0 AND is_correct=0 AND length(model_output) > 200 AND model_name IN (%s)" % marks, FRONTIER6):
        if qtext in items:
            out[cat.capitalize() if cat != "computer science" else "Computer science"].append((qtext, pred, ans, rj.unwrap_envelope(outp or "")[:600]))
    return out


def induce(model="grok-4-1-fast-reasoning"):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = model; rr.load_env()
    t1, t2, t3 = rl.load_templates()
    units, items, _, _ = rl.unit_corpora()
    wrong = wrong_answers(items)
    con = open_db(); done = {(k, u) for k, u in con.execute("SELECT kind, unit FROM rubrics")}
    rng = random.Random(42)
    for (kind, unit), (label, qs) in sorted(units.items()):
        if kind != "anchor": continue
        corpus = []
        for q in qs:
            question, options, answer, cot = items[q]
            try: opts = json.loads(options) if options and options.strip().startswith("[") else [o.strip() for o in (options or "").split("|")]
            except Exception: opts = [options or ""]
            ai = (ord(answer[0].upper()) - 65) if answer else -1
            s = "Q: %s\nChoices: %s" % (question, " | ".join("%s) %s%s" % (chr(65 + i), o, " ✓" if i == ai else "") for i, o in enumerate(opts)))
            if cot and cot.strip(): s += "\nCorrect Reasoning: %s" % cot.strip()
            corpus.append(s)
        for new_kind in ("frontier_anchor", "contrastive_anchor"):
            if (new_kind, unit) in done: continue
            partials = []
            for i in range(0, len(corpus), rl.CHUNK):
                prompt = t1.replace("$items", "\n---\n".join(corpus[i:i + rl.CHUNK])).replace("$domainLabel", label)
                if new_kind == "contrastive_anchor":
                    ws = wrong.get(label, []); rng.shuffle(ws)
                    block = "\n---\n".join("Q: %s\nModel chose %s, correct is %s. Response excerpt: %s" % w for w in ws[:N_WRONG])
                    prompt += CONTRAST_INSTRUCTION.replace("$wrong", block or "(none available)")
                partials.append(rr.strip_think(rr.call_judge("", prompt)[0]))
            master = partials[0] if len(partials) == 1 else rr.strip_think(rr.call_judge("", t2.replace("$partials", "\n\n".join(partials)))[0])
            raw = rr.strip_think(rr.call_judge("", t3.replace("$masterGuidelines", master).replace("$domainLabel", label))[0])
            m = re.search(r"\{.*\}", raw, re.S)
            try: obj = json.loads(m.group(0)) if m else {}
            except Exception: obj = {}
            sp, rub = obj.get("system_prompt", ""), obj.get("rubric", "")
            con.execute("INSERT OR REPLACE INTO rubrics VALUES (?,?,?,?,?,?,?)", (new_kind, unit, label, sp, rub, raw, time.time())); con.commit()
            print("induced %s/%s: sp %d ch, rubric %d ch (%d chunks, wrong=%d)" % (new_kind, label, len(sp), len(rub), len(partials), len(wrong.get(label, []))), flush=True)


def rubric_sets():
    sets = {}
    lad = sqlite3.connect("file:%s?mode=ro" % LADDER, uri=True)
    sets["mistral_anchor"] = {l: (sp, rb) for l, sp, rb in lad.execute("SELECT label, system_prompt, rubric FROM rubrics WHERE kind='anchor'")}
    con = open_db()
    for kind in ("frontier_anchor", "contrastive_anchor"):
        sets[kind] = {l: (sp, rb) for l, sp, rb in con.execute("SELECT label, system_prompt, rubric FROM rubrics WHERE kind=?", (kind,))}
    return sets


def leakage_audit(sets):
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    sample = rj.sample_matches(); qids = {int(m[1]) for m in sample}
    opts = {}
    for q, o, a in ev.execute("SELECT question_id, options_json, correct_answer FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        if q in qids and o:
            try: lst = json.loads(o); i = "ABCDEFGHIJ".find((a or "")[:1]); opts[q] = lst[i] if 0 <= i < len(lst) else ""
            except Exception: pass
    def grams(t, n=5):
        w = re.findall(r"[a-z0-9]+", t.lower()); return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    for kind in ("frontier_anchor", "contrastive_anchor"):
        hits = 0
        for label, (sp, rb) in sets[kind].items():
            g = grams(sp + " " + rb)
            for q, o in opts.items():
                if len(o.split()) >= 5 and grams(o) & g: hits += 1
        print("  leakage audit %-18s shared 5-grams with correct options of judged questions: %d -> %s" % (kind, hits, "CLEAN" if hits == 0 else "LEAK"))


def run(pilot, workers):
    p8.load_env()
    sets = rubric_sets(); anchors = r512.anchor_fn(r512.load_graph(r512.snapshot_id("bareq512_s42")))
    route = r512.primary_routing("bareq512_s42"); anc_of = {q: anchors(l) for q, l in route.items()}
    for kind in ARMS: assert len(sets[kind]) >= 14, "%s rubrics missing (%d)" % (kind, len(sets[kind]))
    leakage_audit(sets)
    sample = rj.sample_matches()
    if pilot: sample = sample[:pilot]
    con = open_db(); done = {(m, a) for m, a in con.execute("SELECT match_id, arm FROM verdicts")}
    todo = [(m, arm) for m in sample for arm in ARMS if (m[0], arm) not in done and int(m[1]) in anc_of]
    evals = rj.load_eval_rows([int(m[1]) for m, _ in todo], {m[2] for m, _ in todo} | {m[3] for m, _ in todo})
    print("J6: sample %d | jobs %d (%d calls) | workers %d" % (len(sample), len(todo), 2 * len(todo), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m, arm):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb = evals.get((qid, a)), evals.get((qid, b))
        if ra is None or rb is None: return None
        anc = anc_of[qid]; sp, rub = sets[arm][anc]
        system = rj.SYSTEM_TEMPLATE.replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        raw1 = p8.call(system, rj.build_user_prompt(ra[0], ta, tb)); raw2 = p8.call(system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1); v2, _ = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (mid, arm, a, b, qid, anc, v1, v2, {"Model A": a, "Model B": b}.get(w, w), int(flip), int(inv), raw1, raw2, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, m, arm): (m, arm) for m, arm in todo}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s/%s: %s" % (futs[f][0][0], futs[f][1], str(e)[:120]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 14), row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(todo): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(todo), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    con = open_db()
    V = defaultdict(dict)
    for mid, arm, a, b, q, anc, w, inv in con.execute("SELECT match_id, arm, model_a, model_b, qid, anchor, winner, invalid FROM verdicts"):
        if not inv: V[mid][arm] = (w, a, b, q, anc)
    gen = {r[0]: r[1] for r in sqlite3.connect("file:%s?mode=ro" % GENERIC_SS, uri=True).execute("SELECT match_id, winner FROM verdicts WHERE invalid=0")}
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = {}
    for mid, arms in V.items():
        if not all(a in arms for a in ARMS): continue
        w, a, b, q, anc = arms[ARMS[0]]
        ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = {arm: arms[arm][0] == d for arm in ARMS}; rows[mid]["generic"] = (gen[mid] == d) if mid in gen else None; rows[mid]["anchor"] = anc
    keys = list(rows)
    def stats(x, y, ks):
        ks = [k for k in ks if rows[k][x] is not None and rows[k][y] is not None]
        n = len(ks); px = sum(rows[k][x] for k in ks) / max(1, n); py = sum(rows[k][y] for k in ks) / max(1, n)
        b = sum(rows[k][x] and not rows[k][y] for k in ks); c = sum(rows[k][y] and not rows[k][x] for k in ks)
        return n, px, py, b, c, p8.mcn(b, c)
    print("=== J6: rubric quality — Mistral judge, no reference, %d key-decidable matches with all three arms ===" % len(keys))
    for lab, x, y, tag in (("contrastive vs mistral-induced (PRIMARY)", "contrastive_anchor", "mistral_anchor", "PRIMARY"),
                           ("frontier vs mistral-induced (SECONDARY)", "frontier_anchor", "mistral_anchor", "SECONDARY"),
                           ("contrastive vs frontier", "contrastive_anchor", "frontier_anchor", ""),
                           ("mistral-induced anchor vs generic (SS session)", "mistral_anchor", "generic", ""),
                           ("contrastive vs generic (SS session)", "contrastive_anchor", "generic", "")):
        n, px, py, b, c, p = stats(x, y, keys)
        verdict = ("  -> %s %s" % (tag, "PASS" if (px > py and p < 0.05) else "FAIL")) if tag else ""
        print("  %-46s %.3f vs %.3f (%+.3f) | %d:%d | p=%.4f n=%d%s" % (lab, px, py, px - py, b, c, p, n, verdict))
    disc = [k for k in keys if rows[k]["anchor"] in p8.DISCURSIVE]; quant = [k for k in keys if rows[k]["anchor"] not in p8.DISCURSIVE]
    for lab, ks in (("discursive", disc), ("quantitative", quant)):
        n, px, py, b, c, p = stats("contrastive_anchor", "mistral_anchor", ks)
        print("  contrastive vs mistral, %-12s n=%4d %.3f vs %.3f (%+.3f) %d:%d p=%.4f" % (lab, n, px, py, px - py, b, c, p))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--induce", action="store_true"); ap.add_argument("--pilot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.induce: induce()
    elif a.analyze: analyze()
    else: run(a.pilot, a.workers); analyze()
