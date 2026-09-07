"""RUBRIC-GRANULARITY LADDER — PRE-REGISTERED (2026-09-07).

WHY. The campaign proved cell rubrics beat a generic judge (McNemar p = 0.0001,
cross-family) and beat the WRONG cell's rubric (p = 0.006, monotone
cell >= sibling >= random). What remains unknown is the SHAPE of the specificity
curve — the thesis's own axis: how specific is specific enough? This experiment
induces rubrics at ANCHOR (14) and STRATUM (20) granularity with the SAME 3-phase
pipeline that produced the frozen leaf rubrics, and judges one paired sample under
the full ladder: generic < anchor < stratum < leaf.

ARMS (judge Mistral-Large-3; template machinery byte-identical via rejudge_grok):
  leaf     = x12 match_history verdicts (existing, paid)
  generic  = rubric_contrast.db mistral/generic arm (existing, paid)
  anchor   = NEW: rubric induced from the match's anchor
  stratum  = NEW: rubric induced from the match's stratum (strata_profile_v1)
Sample S_ladder: seeded uniform 2,000 of the 9,144 x12 MAIN matches (seed 555).
New spend: 2 arms x 2,000 matches x 2 orders = 8,000 judge calls, plus ~900
induction calls (14 + 20 units, 3-phase).

INDUCTION, frozen here:
- Prompts extracted AT RUNTIME from JudgePrompts.kt (induceBatchGuidelines,
  synthesizeGlobalGuidelines, synthesizeFinalJudge) — the same templates that
  built the frozen leaf rubrics; same judge model; chunks of 25 items with
  correct-option check-mark and cot reasoning, exactly as TaxonomyJudgeService
  assembles them.
- Unit corpora: TRAIN-SIDE questions only (reserved pool excluded by eval-id ->
  text join), assigned to leaves by nearest-leaf-centroid (max cosine of the
  cached embedding's first-256 MRL slice against leaf vmfMu) — DISCLOSED
  approximation of production routing (the pipeline's own centroid-routing
  validation metric). Unit corpus capped at 150 seeded-sampled questions
  (leaf induction used whole cells of ~60-95; the cap keeps chunk counts
  comparable). Stratum domainLabel = "<Anchor>: <member leaf labels>".

REGISTRATION (analysis = --analyze run unchanged; key-decidable = verdict correct
iff it names the GT-correct model, TIE/INVALID wrong; all on S_ladder):
  PRIMARY, CONFIRMED iff BOTH:
    (a) leaf > anchor: one-sided exact McNemar p < 0.05;
    (b) monotone point estimates acc_generic <= acc_anchor <= acc_stratum <= acc_leaf.
  SECONDARIES (descriptive): leaf-minus-stratum gap with bootstrap CI (the knee —
    small gap favors stratum-granular rubrics for a v2 tree); anchor-minus-generic
    gap (does any domain context help); per-anchor breakdown (exploratory).
  DISCLOSURES: every prior experiment on this database is committed and public
  (rubric contrast, H7 swap incl. sibling~random, verbosity work); the sample seed,
  corpus rule, and caps above are fixed before any induction or verdict exists;
  leaf rubrics were induced at freeze time by the Kotlin pipeline, anchor/stratum
  rubrics now by this port of the same prompts — same model, same phases.

Run:  python tools/analysis/rubric_ladder.py --induce
      python tools/analysis/rubric_ladder.py --arm anchor|stratum
      python tools/analysis/rubric_ladder.py --analyze
Cache: experiment_results/x12_crossdomain/rubric_ladder.db (resumable).
"""
import sys, os, re, json, math, sqlite3, random, time, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc

DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_ladder.db")
STRATA = os.path.join(ROOT, "experiment_configs", "strata_profile_v1.json")
PROMPTS_KT = os.path.join(ROOT, "src", "main", "kotlin", "taxonomy", "prompts", "JudgePrompts.kt")
SEED_SAMPLE, SEED_CORPUS, N_SAMPLE, CORPUS_CAP, CHUNK = 555, 556, 2000, 150, 25


# ── template extraction (same discipline as rejudge_grok) ─────────────────────
def _extract_fun_template(src, fun_name):
    i = src.index("fun %s(" % fun_name)
    j = src.index('"""', i)
    k = src.index('"""', j + 3)
    return src[j + 3:k]


def load_templates():
    src = open(PROMPTS_KT, encoding="utf-8").read()
    t1 = _extract_fun_template(src, "induceBatchGuidelines")
    t2 = _extract_fun_template(src, "synthesizeGlobalGuidelines")
    t3 = _extract_fun_template(src, "synthesizeFinalJudge")
    assert "$items" in t1 and "$domainLabel" in t1
    assert "$partials" in t2
    assert "$masterGuidelines" in t3 and "$domainLabel" in t3
    return t1, t2, t3


# ── unit membership (nearest-leaf-centroid on train side) ─────────────────────
def unit_corpora():
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []):
            parent[c] = n["id"]

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    leaves = [n for n in nodes.values() if not n.get("childIds")]
    spec = json.load(open(STRATA, encoding="utf-8"))
    leaf2stratum = {l: s["id"] for s in spec["strata"] for l in s["leafIds"]}
    stratum_label = {}
    for s in spec["strata"]:
        labs = [nodes[l]["label"] for l in s["leafIds"]]
        stratum_label[s["id"]] = "%s: %s" % (s["anchor"], " / ".join(labs))[:220]

    # reserved texts (eval id-space -> text, per the id-space repair rule)
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    reserved_ids = set()
    import csv
    with open(os.path.join(ROOT, "reserved_leaf_assignments.csv"), newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            reserved_ids.add(int(row["question_id"]))
    q_marks = ",".join("?" * len(reserved_ids))
    reserved_texts = {r[0] for r in ev.execute(
        "SELECT DISTINCT question_text FROM eval_results WHERE question_id IN (%s)" % q_marks,
        list(reserved_ids))}

    emb = sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "embeddings_cache.db"), uri=True)
    mp = sqlite3.connect("file:%s?mode=ro" % rj.SNAP_DB.replace("snapshots_frozen.db", "mmlu_pro_dataset_cache_v2.db")
                         if "snapshots_frozen" in rj.SNAP_DB else
                         "file:%s?mode=ro" % os.path.join(ROOT, "mmlu_pro_dataset_cache_v2.db"), uri=True)
    items = {r[0]: (r[0], r[1], r[2], r[3]) for r in mp.execute(
        "SELECT question, options, answer, cot_content FROM mmlu_pro")}

    mus = [(l["id"], l["vmfMu"]) for l in leaves]

    def best_leaf(vec):
        v = vec[:256]
        nrm = math.sqrt(sum(x * x for x in v)) or 1.0
        v = [x / nrm for x in v]
        bi, bs = None, -2.0
        for lid, mu in mus:
            s = sum(a * b for a, b in zip(v, mu))
            if s > bs:
                bs, bi = s, lid
        return bi

    by_anchor, by_stratum = defaultdict(list), defaultdict(list)
    n_train = n_skipped = 0
    for qtext, vecraw in emb.execute("SELECT query, vector FROM embeddings"):
        if qtext in reserved_texts or qtext not in items:
            n_skipped += 1
            continue
        try:
            vec = json.loads(vecraw) if isinstance(vecraw, (str, bytes)) else list(vecraw)
        except Exception:
            n_skipped += 1
            continue
        lid = best_leaf(vec)
        n_train += 1
        by_anchor[anchor_of(lid)].append(qtext)
        sid = leaf2stratum.get(lid)
        if sid:
            by_stratum[sid].append(qtext)
    print("train questions assigned: %d (skipped %d)" % (n_train, n_skipped))
    rng = random.Random(SEED_CORPUS)
    units = {}
    for a, qs in by_anchor.items():
        qs = sorted(qs)
        rng.shuffle(qs)
        units[("anchor", a)] = (a, qs[:CORPUS_CAP])
    for sid, qs in by_stratum.items():
        qs = sorted(qs)
        rng.shuffle(qs)
        units[("stratum", sid)] = (stratum_label[sid], qs[:CORPUS_CAP])
    return units, items, anchor_of, leaf2stratum


def open_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS rubrics (
        kind TEXT, unit TEXT, label TEXT, system_prompt TEXT, rubric TEXT,
        raw TEXT, ts REAL, PRIMARY KEY (kind, unit))""")
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, node_id TEXT,
        unit TEXT, vote1 TEXT, vote2_raw TEXT, winner TEXT,
        flip INTEGER, invalid INTEGER, ts REAL, PRIMARY KEY (match_id, arm))""")
    con.commit()
    return con


def induce():
    env = rc.load_env()
    endpoint = env["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    key = env["AZURE_AI_API_KEY"]
    t1, t2, t3 = load_templates()
    units, items, _, _ = unit_corpora()
    con = open_db()
    done = {(k, u) for k, u in con.execute("SELECT kind, unit FROM rubrics")}
    for (kind, unit), (label, qs) in sorted(units.items()):
        if (kind, unit) in done:
            continue
        corpus = []
        for q in qs:
            question, options, answer, cot = items[q]
            try:
                opts = json.loads(options) if options and options.strip().startswith("[") else [o.strip() for o in (options or "").split("|")]
            except Exception:
                opts = [options or ""]
            ai = (ord(answer[0].upper()) - 65) if answer else -1
            choices = " | ".join(
                "%s) %s%s" % (chr(65 + i), o, " ✓" if i == ai else "")
                for i, o in enumerate(opts))
            s = "Q: %s\nChoices: %s" % (question, choices)
            if cot and cot.strip():
                s += "\nCorrect Reasoning: %s" % cot.strip()
            corpus.append(s)
        partials = []
        for i in range(0, len(corpus), CHUNK):
            batch = "\n---\n".join(corpus[i:i + CHUNK])
            prompt = t1.replace("$items", batch).replace("$domainLabel", label)
            partials.append(rc.call_judge(endpoint, key, "Mistral-Large-3", "", prompt))
        master = partials[0] if len(partials) == 1 else rc.call_judge(
            endpoint, key, "Mistral-Large-3", "",
            t2.replace("$partials", "\n\n".join(partials)))
        raw = rc.call_judge(endpoint, key, "Mistral-Large-3", "",
                            t3.replace("$masterGuidelines", master).replace("$domainLabel", label))
        m = re.search(r"\{.*\}", raw, re.S)
        obj = json.loads(m.group(0)) if m else {}
        sp, rub = obj.get("system_prompt", ""), obj.get("rubric", "")
        con.execute("INSERT OR REPLACE INTO rubrics VALUES (?,?,?,?,?,?,?)",
                    (kind, unit, label, sp, rub, raw, time.time()))
        con.commit()
        print("induced %s/%s: sp %d ch, rubric %d ch (%d chunks)"
              % (kind, unit, len(sp), len(rub), len(partials)), flush=True)


def sample_matches():
    con = sqlite3.connect("file:%s?mode=ro" % rc.X12_DB, uri=True)
    rows = con.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=? ORDER BY id", (rj.SNAP_MAIN,)).fetchall()
    rng = random.Random(SEED_SAMPLE)
    rows = rows[:]
    rng.shuffle(rows)
    return rows[:N_SAMPLE]


def run_arm(arm):
    assert arm in ("anchor", "stratum")
    env = rc.load_env()
    endpoint = env["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    key = env["AZURE_AI_API_KEY"]
    con = open_db()
    rubrics = {(k, u): (sp, rub) for k, u, sp, rub in con.execute(
        "SELECT kind, unit, system_prompt, rubric FROM rubrics")}
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []):
            parent[c] = n["id"]

    def anchor_of(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    spec = json.load(open(STRATA, encoding="utf-8"))
    leaf2stratum = {l: s["id"] for s in spec["strata"] for l in s["leafIds"]}

    def unit_for(nid):
        return ("anchor", anchor_of(nid)) if arm == "anchor" else ("stratum", leaf2stratum[nid])

    sample = sample_matches()
    done = {r[0] for r in con.execute("SELECT match_id FROM verdicts WHERE arm=?", (arm,))}
    todo = [m for m in sample if m[0] not in done]
    print("%s: sample %d | cached %d | to judge %d (%d calls)"
          % (arm, len(sample), len(sample) - len(todo), len(todo), 2 * len(todo)), flush=True)
    if not todo:
        return
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()

    def sysprompt_for(nid):
        sp, rub = rubrics[unit_for(nid)]
        base = (rj.SYSTEM_TEMPLATE.replace("$systemPrompt", sp or "You are an expert academic evaluator.")
                .replace("$rubric", rub or "Grade the response based on domain correctness, precision, and logical reasoning."))
        return base + "\n\n" + rj.SCHEMA_INSTRUCTION

    def one(m):
        mid, qid, ma, mb, nid = m
        qid = int(qid)
        ra, rb = evals.get((qid, ma)), evals.get((qid, mb))
        if ra is None or rb is None:
            return None
        ta = rj.robust_trace(ra[2], ra[3], ra[1])
        tb = rj.robust_trace(rb[2], rb[3], rb[1])
        system = sysprompt_for(nid)
        raw1 = rc.call_judge(endpoint, key, "Mistral-Large-3", system, rj.build_user_prompt(ra[0], ta, tb))
        raw2 = rc.call_judge(endpoint, key, "Mistral-Large-3", system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1)
        v2, _ = rj.parse_judge(raw2)
        gw, flip, invalid = rj.combine_orders(v1, v2)
        name = {"Model A": ma, "Model B": mb}.get(gw, gw)
        return (mid, arm, ma, mb, nid, unit_for(nid)[1], v1, v2, name, int(flip), int(invalid), time.time())

    n_ok = n_err = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                n_err += 1
                print("  ERROR match %s: %s" % (futs[fut][0], e), flush=True)
                continue
            if row is None:
                continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 12), row)
                if i % 100 == 0:
                    con.commit()
                    print("  %d/%d" % (i, len(todo)), flush=True)
            n_ok += 1
    con.commit()
    print("done: ok %d errors %d" % (n_ok, n_err))


def analyze():
    con = open_db()
    x12 = sqlite3.connect("file:%s?mode=ro" % rc.X12_DB, uri=True)
    meta = {r[0]: (int(r[1]), r[2], r[3]) for r in x12.execute(
        "SELECT id, eval_question_id, model_a, model_b FROM match_history")}
    leafw = {r[0]: ("TIE" if r[2] else r[1]) for r in x12.execute(
        "SELECT id, winner, is_tie FROM match_history WHERE condition='MAIN' AND snapshot_id=?",
        (rj.SNAP_MAIN,))}
    cache = sqlite3.connect("file:%s?mode=ro" % rc.CACHE_DB, uri=True)
    genw = {r[0]: r[1] for r in cache.execute(
        "SELECT match_id, winner FROM verdicts WHERE judge='mistral' AND rubric='generic' AND invalid=0")}
    arms = {a: {r[0]: r[1] for r in con.execute(
        "SELECT match_id, winner FROM verdicts WHERE arm=? AND invalid=0", (a,))}
        for a in ("anchor", "stratum")}
    models = sorted({m for q, a, b in meta.values() for m in (a, b)})
    gt = rc.gt_correct([meta[m][0] for m in leafw], set(models))

    def dw(mid):
        q, a, b = meta[mid]
        ca, cb = gt.get((q, a)), gt.get((q, b))
        if ca is None or cb is None or ca == cb:
            return None
        return a if ca else b

    sample = [m[0] for m in sample_matches()]
    common = [mid for mid in sample
              if mid in leafw and mid in genw and mid in arms["anchor"] and mid in arms["stratum"]
              and dw(mid) is not None]
    acc = {}
    win = {"generic": genw, "anchor": arms["anchor"], "stratum": arms["stratum"], "leaf": leafw}
    for name, w in win.items():
        acc[name] = sum(1 for mid in common if w[mid] == dw(mid)) / max(1, len(common))
    print("=== LADDER (S_ladder, key-decidable n=%d, fully paired) ===" % len(common))
    for name in ("generic", "anchor", "stratum", "leaf"):
        print("  %-8s %.3f" % (name, acc[name]))
    from math import comb
    b = sum(1 for mid in common if leafw[mid] == dw(mid) and arms["anchor"][mid] != dw(mid))
    c = sum(1 for mid in common if arms["anchor"][mid] == dw(mid) and leafw[mid] != dw(mid))
    p_one = sum(comb(b + c, k) for k in range(b, b + c + 1)) / 2 ** (b + c) if b + c else 1.0
    print("PRIMARY (a) leaf > anchor: discordant %d:%d, one-sided McNemar p = %.4f %s"
          % (b, c, p_one, "PASS" if p_one < 0.05 else "FAIL"))
    mono = acc["generic"] <= acc["anchor"] <= acc["stratum"] <= acc["leaf"]
    print("PRIMARY (b) monotone generic<=anchor<=stratum<=leaf: %s" % ("PASS" if mono else "FAIL"))
    rng = random.Random(42)
    diffs = []
    for _ in range(2000):
        bs = [common[rng.randrange(len(common))] for _ in range(len(common))]
        diffs.append(sum(1 for mid in bs if leafw[mid] == dw(mid)) / len(bs)
                     - sum(1 for mid in bs if arms["stratum"][mid] == dw(mid)) / len(bs))
    diffs.sort()
    print("SECONDARY knee: leaf - stratum = %+.3f CI95 [%+.3f, %+.3f]"
          % (acc["leaf"] - acc["stratum"], diffs[50], diffs[1949]))
    print("SECONDARY context: anchor - generic = %+.3f" % (acc["anchor"] - acc["generic"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--induce", action="store_true")
    ap.add_argument("--arm", choices=["anchor", "stratum"])
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.induce:
        induce()
    elif a.arm:
        run_arm(a.arm)
    elif a.analyze:
        analyze()
    else:
        ap.error("need --induce, --arm or --analyze")
