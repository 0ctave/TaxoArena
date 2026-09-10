"""RUBRIC KIT — K1 failure catalogue + K2 knowledge card + K3 worked neighbours per leaf of the clean
bareq512_s42 tree, and the RK-1 test (docs/rubric_v2_design.md; registered before any call).

Material is TRAIN-side only: the promoted tree was built with the pool of record withheld, so every
leaf's queryIds are construction-side questions; wrong answers come from eval rows with is_reserved=0;
neighbours are retrieved among the leaf's train questions. The judged (reserved) question never enters
induction or retrieval. Leakage audit: no shared 5-gram between kit text / neighbour material and the
correct option of any judged question (neighbours that would share one are dropped at retrieval).

RK-1 (registered): STACK-v2 (reference + v2 mechanics + anchor rubric) vs STACK-v2 + kit (K2 card and K1
catalogue appended to the system prompt; K3 two worked neighbours before the question), both arms judged
fresh and interleaved in one session, Mistral, R3's 1,980 matches. PRIMARY: kit > STACK-v2 by +1pp at
paired McNemar p < 0.05 on key-decidable; SECONDARY: gain in {Math, Physics, Chemistry, Engineering,
Computer science} > gain in the discursive anchors. Prediction: +1 to +3pp, quantitative-led.

  python tools/analysis/rubric_kit.py --induce [--pilot N]      # ~174 grok-reasoning calls
  python tools/analysis/rubric_kit.py --neighbours               # zero calls
  python tools/analysis/rubric_kit.py --judge [--pilot N] [--workers N]   # ~8k Mistral calls
  python tools/analysis/rubric_kit.py --analyze
"""
import os, sys, re, json, time, random, sqlite3, struct, argparse, threading
from collections import defaultdict
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
import prompt_v2

TREE = "bareq512_s42"
KIT_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_kit.db")
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_kit.db")
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
FRONTIER6 = ["gpt-4o-2024-08-06", "gemini-3.1-pro_5-shots", "iask_pro", "arx_0314", "deepseek-chat-v2_5", "Qwen1.5-72B-Chat"]
N_CARD_ITEMS, N_WRONG, N_NEIGH = 40, 20, 2
QUANT = {"Math", "Physics", "Chemistry", "Engineering", "Computer science"}

CARD_PROMPT = """Task: build the KNOWLEDGE CARD of the specialised subdomain "$leaf" (within $anchor) from the solved problems below.

[Solved problems]
$items

[Instructions]
List the facts, formulas, definitions, sign and unit conventions, boundary conditions and standard results that
correct answers in this subdomain rely on. Requirements:
- At most 12 items, each one line, each a GENERAL, CHECKABLE statement (a formula with its variables named, a
  definition, a rule with its condition of validity).
- Do NOT restate any problem, any option text, or any problem-specific number or answer.
- Prefer what distinguishes this subdomain from its neighbours.
Output only a "- " bullet list."""

CATALOGUE_PROMPT = """Task: build the FAILURE CATALOGUE of the specialised subdomain "$leaf" (within $anchor) from real wrong answers
given by strong models to problems of this subdomain.

[Wrong answers]
$wrong

[Instructions]
Derive the 5 to 8 recurrent failure modes. For each give: (a) the error in one line, (b) the tell-tale sign a
judge can spot in a response, (c) the check that exposes it. General patterns only: do NOT restate any
problem, option text, or problem-specific number. Output only a numbered list."""


def open_kit():
    con = sqlite3.connect(KIT_DB)
    con.execute("CREATE TABLE IF NOT EXISTS kit (leaf TEXT, kind TEXT, label TEXT, anchor TEXT, text TEXT, raw TEXT, n_items INTEGER, ts REAL, PRIMARY KEY (leaf, kind))")
    con.execute("CREATE TABLE IF NOT EXISTS neighbours (qid INTEGER PRIMARY KEY, leaf TEXT, payload TEXT)")
    con.commit()
    return con


def leaf_material():
    """leaf -> dict(label, anchor, items=[(question, options, answer, cot)], texts=set)"""
    nodes = r512.load_graph(r512.snapshot_id(TREE)); anchor = r512.anchor_fn(nodes)
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    raw = {i: t for i, t in emb.execute("SELECT id, raw_text FROM queries")}
    mp = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    rows = {r[0]: r for r in mp.execute("SELECT question, options, answer, cot_content FROM mmlu_pro")}
    out = {}
    for n in nodes.values():
        if n.get("childIds"): continue
        items = [rows[raw[q]] for q in n.get("queryIds", []) if raw.get(q) in rows]
        out[n["id"]] = {"label": n["label"], "anchor": anchor(n["id"]), "items": items, "texts": {it[0] for it in items}}
    return out


def fmt_item(it, with_cot=True, cot_chars=700):
    question, options, answer, cot = it
    try: opts = json.loads(options) if options and options.strip().startswith("[") else [o.strip() for o in (options or "").split("|")]
    except Exception: opts = [options or ""]
    ai = (ord(answer[0].upper()) - 65) if answer else -1
    s = "Q: %s\nChoices: %s" % (question, " | ".join("%s) %s%s" % (chr(65 + i), o, " (correct)" if i == ai else "") for i, o in enumerate(opts)))
    if with_cot and cot and cot.strip(): s += "\nReference reasoning: %s" % cot.strip()[:cot_chars]
    return s


def wrong_by_text():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    out = defaultdict(list); marks = ",".join("?" * len(FRONTIER6))
    for qtext, pred, ans, outp in ev.execute("SELECT question_text, pred, gt_answer, model_output FROM eval_results WHERE is_reserved=0 AND is_correct=0 AND length(model_output) > 200 AND model_name IN (%s)" % marks, FRONTIER6):
        out[qtext].append((pred, ans, rj.unwrap_envelope(outp or "")[:500]))
    return out


def induce(pilot):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-reasoning"; rr.load_env()
    mat = leaf_material(); wrong = wrong_by_text(); con = open_kit()
    done = {(l, k) for l, k in con.execute("SELECT leaf, kind FROM kit")}
    rng = random.Random(42); leaves = sorted(mat)
    if pilot: leaves = leaves[:pilot]
    for l in leaves:
        m = mat[l]; items = m["items"][:]; rng.shuffle(items)
        if (l, "card") not in done:
            prompt = CARD_PROMPT.replace("$leaf", m["label"]).replace("$anchor", m["anchor"]).replace("$items", "\n---\n".join(fmt_item(it) for it in items[:N_CARD_ITEMS]))
            raw = rr.strip_think(rr.call_judge("", prompt)[0])
            con.execute("INSERT OR REPLACE INTO kit VALUES (?,?,?,?,?,?,?,?)", (l, "card", m["label"], m["anchor"], raw.strip(), raw, min(len(items), N_CARD_ITEMS), time.time())); con.commit()
            print("card      %s (%s): %d ch from %d items" % (m["label"][:40], m["anchor"], len(raw), min(len(items), N_CARD_ITEMS)), flush=True)
        if (l, "catalogue") not in done:
            ws = [(it[0], w) for it in items for w in wrong.get(it[0], [])]; rng.shuffle(ws)
            block = "\n---\n".join("Q: %s\nChose %s, correct %s. Excerpt: %s" % (q, w[0], w[1], w[2]) for q, w in ws[:N_WRONG])
            prompt = CATALOGUE_PROMPT.replace("$leaf", m["label"]).replace("$anchor", m["anchor"]).replace("$wrong", block or "(no wrong answers available)")
            raw = rr.strip_think(rr.call_judge("", prompt)[0])
            con.execute("INSERT OR REPLACE INTO kit VALUES (?,?,?,?,?,?,?,?)", (l, "catalogue", m["label"], m["anchor"], raw.strip(), raw, min(len(ws), N_WRONG), time.time())); con.commit()
            print("catalogue %s (%s): %d ch from %d wrong answers" % (m["label"][:40], m["anchor"], len(raw), min(len(ws), N_WRONG)), flush=True)


def grams(t, n=5):
    w = re.findall(r"[a-z0-9]+", t.lower()); return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def neighbours():
    """K3 for every R3 question: top-2 train questions of its routed leaf by cosine on the 512-slice, option-overlap filtered."""
    mat = leaf_material(); route = r512.primary_routing(TREE)
    sample = rj.sample_matches(); qids = sorted({int(m[1]) for m in sample})
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    qtext, copt = {}, {}
    for q, t, o, a in ev.execute("SELECT question_id, question_text, options_json, gt_answer FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        if q in set(qids):
            qtext[q] = t
            try: lst = json.loads(o); i = "ABCDEFGHIJ".find((a or "")[:1]); copt[q] = lst[i] if 0 <= i < len(lst) else ""
            except Exception: copt[q] = ""
    want = set(qtext.values()) | {t for m in mat.values() for t in m["texts"]}
    emb = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True); vec = {}
    for t, blob in emb.execute("SELECT query, vector FROM embeddings"):
        if t in want and isinstance(blob, bytes) and len(blob) % 4 == 0:
            v = np.frombuffer(blob, ">f4").astype(np.float64)[:512]; n = np.linalg.norm(v)
            if n > 0: vec[t] = v / n
    con = open_kit(); n_ok = n_drop = 0
    for q in qids:
        l = route.get(q); t = qtext.get(q)
        if l is None or t not in vec or l not in mat: continue
        cands = [it for it in mat[l]["items"] if it[0] in vec]
        if not cands: continue
        M = np.stack([vec[it[0]] for it in cands]); sims = M @ vec[t]
        order = np.argsort(-sims); chosen = []
        og = grams(copt.get(q, "")) if len((copt.get(q, "") or "").split()) >= 5 else set()
        for i in order:
            it = cands[i]
            if og and (grams(fmt_item(it)) & og): n_drop += 1; continue
            chosen.append({"sim": float(sims[i]), "text": fmt_item(it, cot_chars=900)})
            if len(chosen) == N_NEIGH: break
        con.execute("INSERT OR REPLACE INTO neighbours VALUES (?,?,?)", (q, l, json.dumps(chosen))); n_ok += 1
    con.commit()
    print("neighbours: %d questions with worked examples, %d candidates dropped for option overlap" % (n_ok, n_drop))


def leakage_audit(kit, sample):
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True); qids = {int(m[1]) for m in sample}
    opts = {}
    for q, o, a in ev.execute("SELECT question_id, options_json, gt_answer FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        if q in qids and o:
            try: lst = json.loads(o); i = "ABCDEFGHIJ".find((a or "")[:1]); opts[q] = lst[i] if 0 <= i < len(lst) else ""
            except Exception: pass
    og = {q: grams(o) for q, o in opts.items() if len(o.split()) >= 5}
    hits = 0
    for (l, kind), text in kit.items():
        g = grams(text)
        hits += sum(1 for q, gg in og.items() if gg & g)
    print("  leakage audit (kit text vs correct options of judged questions, 5-grams): %d -> %s" % (hits, "CLEAN" if hits == 0 else "LEAK"))
    return hits == 0


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, leaf TEXT, "
                "vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.commit()
    return con


def judge(pilot, workers):
    p8.load_env(); rref.set_reference("grok-reasoning"); refs = rref.references()
    rubrics = sj.anchor_rubrics(); route = r512.primary_routing(TREE); anchors = sj.routed_anchor()
    kcon = open_kit(); kit = {(l, k): t for l, k, t in kcon.execute("SELECT leaf, kind, text FROM kit")}
    neigh = {q: json.loads(p) for q, p in kcon.execute("SELECT qid, payload FROM neighbours")}
    sample = rj.sample_matches()
    assert leakage_audit(kit, sample), "kit leaks option text — not judging"
    leaves_needed = {route[int(m[1])] for m in sample if int(m[1]) in route}
    missing = [l for l in leaves_needed if (l, "card") not in kit or (l, "catalogue") not in kit]
    assert not missing, "kit missing for %d leaves" % len(missing)
    if pilot: sample = sample[:pilot]
    cache = open_cache(); done = {(m, a) for m, a in cache.execute("SELECT match_id, arm FROM verdicts")}
    todo = [(m, arm) for m in sample for arm in ("stackv2", "kit") if (m[0], arm) not in done]
    evals = rj.load_eval_rows([int(m[1]) for m, _ in todo], {m[2] for m, _ in todo} | {m[3] for m, _ in todo})
    print("RK-1: sample %d | jobs %d (%d calls) | workers %d | neighbours for %d questions" % (len(sample), len(todo), 2 * len(todo), workers, len(neigh)), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(m, arm):
        mid, qid, a, b, *_ = m; qid = int(qid)
        ra, rb, ref, anc, leaf = evals.get((qid, a)), evals.get((qid, b)), refs.get(qid), anchors.get(qid), route.get(qid)
        if ra is None or rb is None or ref is None or anc is None or leaf is None: return None
        sp, rb_ = rubrics[anc]
        system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rb_)
        q = rref.with_reference(ra[0], ref)
        if arm == "kit":
            system += ("\n\nCell knowledge card — facts that must hold in this subdomain (\"%s\"):\n%s\n\nCell failure catalogue — how answers in this subdomain typically go wrong:\n%s"
                       % (leaf and kcon.execute("SELECT label FROM kit WHERE leaf=? AND kind='card'", (leaf,)).fetchone()[0], kit[(leaf, "card")], kit[(leaf, "catalogue")]))
            ex = neigh.get(qid, [])
            if ex: q = "[Two solved examples from the same subdomain — training problems, for reference only; the judged question below is different]\n%s\n\n%s" % ("\n---\n".join(e["text"] for e in ex), q)
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


def analyze():
    cache = open_cache(); V = defaultdict(dict)
    for mid, arm, a, b, q, anc, w, inv, fl in cache.execute("SELECT match_id, arm, model_a, model_b, qid, anchor, winner, invalid, flip FROM verdicts"):
        if not inv: V[mid][arm] = (w, a, b, q, anc, fl)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    G = {(q, m): bool(c) for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results")}
    rows = {}
    for mid, arms in V.items():
        if "stackv2" not in arms or "kit" not in arms: continue
        w, a, b, q, anc, _ = arms["kit"]; ca, cb = G.get((q, a)), G.get((q, b))
        if ca is None or cb is None or ca == cb: continue
        d = a if ca else b
        rows[mid] = {"kit": w == d, "base": arms["stackv2"][0] == d, "anchor": anc, "top": a in sj.TOP4 and b in sj.TOP4}
    def stats(ks):
        n = len(ks); pk = sum(rows[k]["kit"] for k in ks) / max(1, n); pb = sum(rows[k]["base"] for k in ks) / max(1, n)
        b = sum(rows[k]["kit"] and not rows[k]["base"] for k in ks); c = sum(rows[k]["base"] and not rows[k]["kit"] for k in ks)
        return n, pk, pb, b, c, p8.mcn(b, c)
    keys = list(rows); n, pk, pb, b, c, p = stats(keys)
    print("=== RK-1: STACK-v2 + kit (card + catalogue + 2 worked neighbours) vs STACK-v2, Mistral, %d key-decidable paired ===" % n)
    print("  ALL           kit %.3f vs base %.3f (%+.3f) | %d:%d | p=%.4f -> PRIMARY %s" % (pk, pb, pk - pb, b, c, p, "PASS" if (pk - pb >= 0.01 and p < 0.05) else "FAIL"))
    n, pk, pb, b, c, p = stats([k for k in keys if rows[k]["top"]]); print("  TOP-CLUSTER   kit %.3f vs base %.3f (%+.3f) | %d:%d | p=%.4f" % (pk, pb, pk - pb, b, c, p))
    gq = stats([k for k in keys if rows[k]["anchor"] in QUANT]); gd = stats([k for k in keys if rows[k]["anchor"] not in QUANT])
    print("  quantitative  n=%4d kit %.3f vs base %.3f (%+.3f) %d:%d p=%.4f" % (gq[0], gq[1], gq[2], gq[1] - gq[2], gq[3], gq[4], gq[5]))
    print("  discursive    n=%4d kit %.3f vs base %.3f (%+.3f) %d:%d p=%.4f" % (gd[0], gd[1], gd[2], gd[1] - gd[2], gd[3], gd[4], gd[5]))
    print("  SECONDARY (quantitative gain > discursive gain): %s" % ("PASS" if (gq[1] - gq[2]) > (gd[1] - gd[2]) else "FAIL"))
    by = defaultdict(list)
    for k in keys: by[rows[k]["anchor"]].append(k)
    for anc in sorted(by, key=lambda a: -(stats(by[a])[1] - stats(by[a])[2])):
        n, pk, pb, b, c, p = stats(by[anc]); print("     %-18s n=%3d  gain %+.3f  (%d:%d)" % (anc[:18], n, pk - pb, b, c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--induce", action="store_true"); ap.add_argument("--neighbours", action="store_true")
    ap.add_argument("--judge", action="store_true"); ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    if a.induce: induce(a.pilot)
    elif a.neighbours: neighbours()
    elif a.judge: judge(a.pilot, a.workers); analyze()
    elif a.analyze: analyze()
