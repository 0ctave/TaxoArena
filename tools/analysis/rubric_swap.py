"""H7: rubric-swap placebo control + registered length-instruction arm — PRE-REGISTERED.

WHY (2026-09-07). Two claims need hardening. (1) The rubric-value result (cell
rubrics beat generic, McNemar p = 0.0001) is open to the placebo objection: maybe
ANY detailed rubric helps and specificity is irrelevant. The kill test judges the
same matches under the WRONG cell's judge (sibling anchor / random anchor).
(2) The verbosity-bias mechanism (beta_len = +0.39/1k chars; length-matched refits
recover near-GT top-cluster order) was found POST-HOC; a length-disciplined rubric
arm converts it into a registered, falsifiable prediction.

ARMS (judge Mistral-Large-3, byte-identical template machinery via rejudge_grok;
existing paid arms reused: CELL = x12 match_history, GENERIC = rubric_contrast.db):
  swap_random   full donor-cell judge (system prompt + rubric) from a DIFFERENT
                anchor; deterministic donor map (seeded shuffle, seed 777, must
                cross anchors). Sample S_main: seeded uniform 2,000 of the 9,144
                x12 MAIN matches (seed 4242).
  swap_sibling  donor leaf from the SAME anchor (next leaf cyclic by id within
                anchor). Sample: S_main[:1000] (same matches -> three-way paired).
  cell_lengthisc  the match's OWN cell judge + an appended length-discipline
                clause (below). Sample S_len: seeded 1,200 (seed 4243) from
                matches with |len(trace_a)-len(trace_b)| >= 400 chars, where the
                length coefficient has leverage. Enrichment uses lengths ONLY.

LENGTH_CLAUSE (verbatim, appended to the cell system prompt before the schema):
  "Length discipline: the length of a response carries NO evidentiary weight.
   A longer answer is not more correct, more rigorous, or more complete for
   being longer. Judge only the correctness and relevance of the content; do
   not reward elaboration, restatement, or padding."

REGISTRATION, frozen here before any new verdict exists. Analysis = --analyze
run unchanged on the completed cache.
  PRIMARY (rubric specificity), CONFIRMED iff BOTH hold:
    (a) on S_main key-decidable matches (verdict correct iff it names the
        GT-correct model; TIE/INVALID wrong), one-sided exact McNemar
        CELL > swap_random at p < 0.05;
    (b) monotone point estimates acc_cell >= acc_sibling >= acc_random on the
        shared 1,000-match subset.
    Any other pattern is reported as-is.
  SECONDARY (length instruction), registered directional test:
    on S_len decisive verdicts, delta = beta_len(CELL) - beta_len(cell_lengthisc)
    from the verdict ~ lengthDiff/1k + gtDiff logistic, paired by match;
    SUPPORTED iff delta > 0 with the 95% percentile bootstrap CI (B = 1000,
    seed 42, resampling matches) excluding 0. Descriptive: top-4 BT order
    under the length arm.
  DISCLOSURES: the verbosity mechanism was discovered post-hoc on this same
  x12 database (2026-09-07, disclosed in x12_profile.toml); the enrichment of
  S_len uses response lengths only, never verdicts; donor maps and samples are
  deterministic given the seeds above; expected spend (2000+1000+1200) x 2 =
  8,400 judge calls.

Run:  python tools/analysis/rubric_swap.py --arm swap_random|swap_sibling|cell_lengthisc
      python tools/analysis/rubric_swap.py --analyze
Cache: experiment_results/x12_crossdomain/rubric_swap.db (match_id, arm) PK;
resumable; INVALID excluded by the registered filter as in the rubric-value test.
"""
import sys, os, json, math, sqlite3, random, time, argparse, threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import rubric_value_contrast as rc

CACHE_DB = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_swap.db")
SEED_MAIN, SEED_LEN, SEED_DONOR = 4242, 4243, 777
N_MAIN, N_SIB, N_LEN, LEN_ENRICH = 2000, 1000, 1200, 400

LENGTH_CLAUSE = (
    "Length discipline: the length of a response carries NO evidentiary weight. "
    "A longer answer is not more correct, more rigorous, or more complete for "
    "being longer. Judge only the correctness and relevance of the content; do "
    "not reward elaboration, restatement, or padding.")


def anchor_maps():
    nodes = rj.load_nodes()
    parent = {}
    for n in nodes.values():
        for c in n.get("childIds", []):
            parent[c] = n["id"]

    def anchor(nid):
        n = nodes[nid]
        while n["depth"] > 1:
            n = nodes[parent[n["id"]]]
        return n["label"]
    leaves = sorted(n["id"] for n in nodes.values() if not n.get("childIds"))
    by_anchor = defaultdict(list)
    for l in leaves:
        by_anchor[anchor(l)].append(l)
    sibling = {}
    for a, ls in by_anchor.items():
        for i, l in enumerate(ls):
            sibling[l] = ls[(i + 1) % len(ls)]
    rng = random.Random(SEED_DONOR)
    shuffled = leaves[:]
    rng.shuffle(shuffled)
    rand_donor = {}
    for i, l in enumerate(leaves):
        j = i
        while anchor(shuffled[j % len(leaves)]) == anchor(l):
            j += 1
        rand_donor[l] = shuffled[j % len(leaves)]
    return nodes, sibling, rand_donor


def samples():
    con = sqlite3.connect("file:%s?mode=ro" % rc.X12_DB, uri=True)
    rows = con.execute(
        "SELECT id, eval_question_id, model_a, model_b, node_id FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=? ORDER BY id", (rj.SNAP_MAIN,)).fetchall()
    con.close()
    rng = random.Random(SEED_MAIN)
    main = rows[:]
    rng.shuffle(main)
    s_main = main[:N_MAIN]
    s_sib = s_main[:N_SIB]
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L = {}
    for q, m, o in ev.execute("SELECT question_id, model_name, model_output FROM eval_results"):
        L[(q, m)] = len(o or "")
    ev.close()
    big = [r for r in rows if abs(L.get((int(r[1]), r[2]), 0) - L.get((int(r[1]), r[3]), 0)) >= LEN_ENRICH]
    rng2 = random.Random(SEED_LEN)
    rng2.shuffle(big)
    s_len = big[:N_LEN]
    return {"swap_random": s_main, "swap_sibling": s_sib, "cell_lengthisc": s_len}


def open_cache():
    con = sqlite3.connect(CACHE_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS verdicts (
        match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, node_id TEXT,
        donor_node TEXT, vote1 TEXT, vote2_raw TEXT, winner TEXT,
        flip INTEGER, invalid INTEGER, ts REAL, PRIMARY KEY (match_id, arm))""")
    con.commit()
    return con


def system_for(arm, node, nodes, sibling, rand_donor):
    if arm == "swap_sibling":
        donor = nodes[sibling[node["id"]]]
        return rj.build_system_prompt(donor), donor["id"]
    if arm == "swap_random":
        donor = nodes[rand_donor[node["id"]]]
        return rj.build_system_prompt(donor), donor["id"]
    if arm == "cell_lengthisc":
        base = rj.build_system_prompt(node)
        assert base.endswith(rj.SCHEMA_INSTRUCTION)
        stem = base[: -len(rj.SCHEMA_INSTRUCTION)]
        return stem + LENGTH_CLAUSE + "\n\n" + rj.SCHEMA_INSTRUCTION, node["id"]
    raise ValueError(arm)


def run(arm):
    env = rc.load_env()
    endpoint = env["AZURE_AI_ENDPOINT"].rstrip("/") + "/models/chat/completions?api-version=2024-05-01-preview"
    key = env["AZURE_AI_API_KEY"]
    nodes, sibling, rand_donor = anchor_maps()
    sample = samples()[arm]
    cache = open_cache()
    done = {r[0] for r in cache.execute("SELECT match_id FROM verdicts WHERE arm=?", (arm,))}
    todo = [m for m in sample if m[0] not in done]
    print("%s: sample %d | cached %d | to judge %d (%d calls)"
          % (arm, len(sample), len(sample) - len(todo), len(todo), 2 * len(todo)))
    if not todo:
        return
    evals = rj.load_eval_rows([int(m[1]) for m in todo], {m[2] for m in todo} | {m[3] for m in todo})
    lock = threading.Lock()
    stats = {"ok": 0, "err": 0}

    def one(m):
        mid, qid, ma, mb, nid = m
        qid = int(qid)
        ra, rb = evals.get((qid, ma)), evals.get((qid, mb))
        if ra is None or rb is None:
            return None
        ta = rj.robust_trace(ra[2], ra[3], ra[1])
        tb = rj.robust_trace(rb[2], rb[3], rb[1])
        system, donor = system_for(arm, nodes[nid], nodes, sibling, rand_donor)
        raw1 = rc.call_judge(endpoint, key, "Mistral-Large-3", system, rj.build_user_prompt(ra[0], ta, tb))
        raw2 = rc.call_judge(endpoint, key, "Mistral-Large-3", system, rj.build_user_prompt(ra[0], tb, ta))
        v1, _ = rj.parse_judge(raw1)
        v2, _ = rj.parse_judge(raw2)
        gw, flip, invalid = rj.combine_orders(v1, v2)
        name = {"Model A": ma, "Model B": mb}.get(gw, gw)
        return (mid, arm, ma, mb, nid, donor, v1, v2, name, int(flip), int(invalid), time.time())

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(one, m): m for m in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                row = fut.result()
            except Exception as e:
                stats["err"] += 1
                print("  ERROR match %s: %s" % (futs[fut][0], e))
                continue
            if row is None:
                continue
            with lock:
                cache.execute("INSERT OR REPLACE INTO verdicts VALUES (%s)" % ",".join("?" * 12), row)
                if i % 50 == 0:
                    cache.commit()
                    print("  %d/%d" % (i, len(todo)), flush=True)
            stats["ok"] += 1
    cache.commit()
    print("done: ok %d errors %d" % (stats["ok"], stats["err"]))


def analyze():
    cache = open_cache()
    con = sqlite3.connect("file:%s?mode=ro" % rc.X12_DB, uri=True)
    cellw = {r[0]: ("TIE" if r[3] else r[2]) for r in con.execute(
        "SELECT id, eval_question_id, winner, is_tie FROM match_history "
        "WHERE condition='MAIN' AND snapshot_id=?", (rj.SNAP_MAIN,))}
    meta = {r[0]: (int(r[1]), r[2], r[3]) for r in con.execute(
        "SELECT id, eval_question_id, model_a, model_b FROM match_history")}
    all_models = sorted({m for q, a, b in meta.values() for m in (a, b)})
    gt = rc.gt_correct([q for q, _, _ in meta.values()], set(all_models))

    def dw(mid):
        q, a, b = meta[mid]
        ca, cb = gt.get((q, a)), gt.get((q, b))
        if ca is None or cb is None or ca == cb:
            return None
        return a if ca else b

    arms = {arm: {r[0]: r[1] for r in cache.execute(
        "SELECT match_id, winner FROM verdicts WHERE arm=? AND invalid=0", (arm,))}
        for arm in ("swap_random", "swap_sibling", "cell_lengthisc")}

    # PRIMARY (a): cell vs random on S_main decidable
    def mcnemar_pairs(armw):
        b = c = n = acc_c = acc_a = 0
        for mid, aw in armw.items():
            d = dw(mid)
            if d is None or mid not in cellw:
                continue
            n += 1
            cok, aok = cellw[mid] == d, aw == d
            acc_c += cok
            acc_a += aok
            if cok and not aok:
                b += 1
            if aok and not cok:
                c += 1
        return n, acc_c, acc_a, b, c
    n, ac, ar, b_, c_ = mcnemar_pairs(arms["swap_random"])
    from math import comb
    p_one = sum(comb(b_ + c_, k) for k in range(b_, b_ + c_ + 1)) / 2 ** (b_ + c_) if b_ + c_ else 1.0
    print("=== PRIMARY (a): cell vs swap_random, S_main key-decidable ===")
    print("n=%d | acc cell %.3f vs random %.3f | discordant %d:%d | one-sided McNemar p = %.4f %s"
          % (n, ac / max(1, n), ar / max(1, n), b_, c_, p_one, "PASS" if p_one < 0.05 else "FAIL"))
    ns, acs, asb, _, _ = mcnemar_pairs({m: w for m, w in arms["swap_sibling"].items()})
    shared = set(arms["swap_sibling"]) & set(arms["swap_random"])
    nr2 = sum(1 for m in shared if dw(m) is not None)
    accs = {"cell": 0, "sib": 0, "rnd": 0}
    for m in shared:
        d = dw(m)
        if d is None:
            continue
        accs["cell"] += cellw.get(m) == d
        accs["sib"] += arms["swap_sibling"][m] == d
        accs["rnd"] += arms["swap_random"][m] == d
    print("=== PRIMARY (b): monotonicity on shared subset (n_dec=%d) ===" % nr2)
    mono = accs["cell"] >= accs["sib"] >= accs["rnd"]
    print("acc cell %.3f >= sibling %.3f >= random %.3f : %s"
          % (accs["cell"] / max(1, nr2), accs["sib"] / max(1, nr2), accs["rnd"] / max(1, nr2),
             "PASS" if mono else "FAIL"))

    # SECONDARY: beta_len difference, paired bootstrap
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    L, G = {}, {}
    for q, m2, o, ok in ev.execute(
            "SELECT question_id, model_name, model_output, is_correct FROM eval_results"):
        L[(q, m2)] = len(o or "")
        G[(q, m2)] = ok or 0

    def xy(armw):
        recs = []
        for mid, w in armw.items():
            q, a, b2 = meta[mid]
            la, lb = L.get((q, a)), L.get((q, b2))
            if la is None or lb is None or w not in (a, b2):
                continue
            recs.append((mid, (la - lb) / 1000.0, G[(q, a)] - G[(q, b2)], 1.0 if w == a else 0.0))
        return recs
    import bias_audit as ba
    len_arm = xy(arms["cell_lengthisc"])
    cell_arm = xy({m: cellw[m] for m in arms["cell_lengthisc"] if m in cellw})
    bl, _ = ba._logit3([(x, g) for _, x, g, _ in len_arm], [y for _, _, _, y in len_arm])
    bc, _ = ba._logit3([(x, g) for _, x, g, _ in cell_arm], [y for _, _, _, y in cell_arm])
    obs = bc[1] - bl[1]
    rng = random.Random(42)
    mids = sorted(set(m for m, *_ in len_arm) & set(m for m, *_ in cell_arm))
    li = {m: r for r in len_arm for m in [r[0]]}
    ci = {m: r for r in cell_arm for m in [r[0]]}
    diffs = []
    for _ in range(1000):
        bs = [mids[rng.randrange(len(mids))] for _ in range(len(mids))]
        b1, _ = ba._logit3([(li[m][1], li[m][2]) for m in bs], [li[m][3] for m in bs])
        b2_, _ = ba._logit3([(ci[m][1], ci[m][2]) for m in bs], [ci[m][3] for m in bs])
        diffs.append(b2_[1] - b1[1])
    diffs.sort()
    lo, hi = diffs[25], diffs[974]
    print("=== SECONDARY: length instruction (S_len, paired n=%d) ===" % len(mids))
    print("beta_len cell %+0.3f vs length-instructed %+0.3f | delta %+0.3f CI95 [%+0.3f, %+0.3f] %s"
          % (bc[1], bl[1], obs, lo, hi, "SUPPORTED" if lo > 0 else "NOT SUPPORTED"))
    top = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]
    rows = [(w, meta[m][1], meta[m][2]) for m, w in arms["cell_lengthisc"].items()
            if meta[m][1] in top and meta[m][2] in top]
    if rows:
        bd = ba._fit(rows, top)
        print("descriptive top-4 under length arm (n=%d): %s"
              % (len(rows), " > ".join(sorted(top, key=lambda m2: -bd[m2]))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=["swap_random", "swap_sibling", "cell_lengthisc"])
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    if a.analyze:
        analyze()
    elif a.arm:
        run(a.arm)
    else:
        ap.error("need --arm or --analyze")
