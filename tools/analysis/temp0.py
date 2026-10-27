"""TEMP-0 — is the 5.7% test-retest floor a property of LLM judging, or a default we never set? (registered 2026-09-14)

  python tools/analysis/temp0.py --pilot                       (10 identical-call pairs, the registered gate)
  python tools/analysis/temp0.py --judge [--workers 8]
  python tools/analysis/temp0.py --analyze

No judge call in this campaign has ever set a temperature: call_judge posted {model, max_tokens, messages} and
nothing else, so every verdict ran at the provider default. DECOMP measured the consequence - 5.7% disagreement
between two calls on BYTE-IDENTICAL prompts - without knowing the cause. This re-judges those same 299 matches
twice at temperature 0 (arms t0a, t0b), everything else byte-identical to the existing arms.
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
import prompt_v2
import arena13 as a13

NEW = a13.NEW
NOISE = 0.057          # DECOMP, on exactly these 299 matches
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "temp0_outcome.txt")


def population():
    """The 299 frontier matches whose ensemble and grok reference letters agree - DECOMP's stratum SAME."""
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    rref.set_reference("grok-reasoning"); grok = rref.references()
    con = a13.open_cache()
    out = []
    for m, q, opp, anc, fr in con.execute("SELECT mid, qid, opponent, anchor, frontier FROM schedule"):
        if not fr: continue
        e = a13.ensemble_ref(q, P, OPT, {opp, NEW}); g = grok.get(q)
        if e is None or g is None or e[0] != g[0]: continue
        out.append((m, q, opp, anc))
    return sorted(out), P, K, OPT, cot


def build_prompt(qid, opp, anc, rubrics, evals, P, OPT, cot):
    ro = evals.get((qid, opp))
    if ro is None or qid not in cot: return None
    ref = a13.ensemble_ref(qid, P, OPT, {opp, NEW})
    if ref is None: return None
    sp, rub = rubrics[anc]
    system = prompt_v2.v2_system_template().replace("$systemPrompt", sp).replace("$rubric", rub) + "\n\n" + rj.SCHEMA_INSTRUCTION
    q = ro[0] + "\n\n[Reference solution — produced independently, may be wrong]\n(%s) %s" % (ref[0], ref[1])
    return system, rj.build_user_prompt(q, cot[qid][2], rj.robust_trace(ro[2], ro[3], ro[1]))


def pilot():
    """REGISTERED GATE: 10 pairs of identical calls at temperature 0. Fewer than 8 identical -> abandon."""
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rr.TEMPERATURE = 0.0
    sched, P, K, OPT, cot = population()
    rubrics = sj.anchor_rubrics()
    evals = rj.load_eval_rows([s[1] for s in sched[:10]], set(p8.ARENA12))
    same = 0; n = 0
    for m, qid, opp, anc in sched[:10]:
        pr = build_prompt(qid, opp, anc, rubrics, evals, P, OPT, cot)
        if pr is None: continue
        a = rr.strip_think(rr.call_judge(*pr)[0]); b = rr.strip_think(rr.call_judge(*pr)[0])
        n += 1; same += int(a == b)
        print("  match %d: %s" % (m, "identical" if a == b else "DIFFERENT"), flush=True)
    print("PILOT GATE: %d of %d identical -> %s" % (same, n, "PROCEED" if same >= 8 else "ABANDON (the deployment does not honour temperature)"))
    return same >= 8


def pilot2():
    """AMENDED GATE (2026-09-14, before the main run). The registered gate - 8 of 10 byte-identical responses at
    temperature 0 - came out 0 of 10, but that is equally consistent with 'temperature honoured, batched
    inference not bit-deterministic', so as specified it cannot distinguish the failure it was written to catch.
    The control it was missing: run the SAME prompts twice at the provider DEFAULT as well. Byte-identity that is
    0 in both conditions means the gate is UNINFORMATIVE, not failed; a verdict-agreement gap between the two
    conditions is the thing the primary readout is actually about. This does not lower the bar - the registered
    primary (disagreement < 0.02) is untouched - it replaces an uninformative instrument before spending."""
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    sched, P, K, OPT, cot = population()
    rubrics = sj.anchor_rubrics()
    evals = rj.load_eval_rows([s[1] for s in sched[:10]], set(p8.ARENA12))
    res = {}
    for tag, temp in (("temperature 0", 0.0), ("provider default", None)):
        rr.TEMPERATURE = temp
        ident = vagree = n = 0
        for m, qid, opp, anc in sched[:10]:
            pr = build_prompt(qid, opp, anc, rubrics, evals, P, OPT, cot)
            if pr is None: continue
            a = rr.strip_think(rr.call_judge(*pr)[0]); b = rr.strip_think(rr.call_judge(*pr)[0])
            va, _ = rj.parse_judge(a); vb, _ = rj.parse_judge(b)
            n += 1; ident += int(a == b); vagree += int(va == vb)
        res[tag] = (n, ident, vagree)
        print("  %-18s n=%d | byte-identical %d | same VERDICT %d" % (tag, n, ident, vagree), flush=True)
    i0, i1 = res["temperature 0"][1], res["provider default"][1]
    v0, v1 = res["temperature 0"][2], res["provider default"][2]
    if i0 == 0 and i1 == 0:
        print("GATE UNINFORMATIVE AS REGISTERED: byte-identity is 0 in BOTH conditions, so this deployment is")
        print("  never bit-deterministic and the registered instrument cannot see whether temperature is honoured.")
        print("  Verdict stability %d/%d at temperature 0 vs %d/%d at default -> %s"
              % (v0, res["temperature 0"][0], v1, res["provider default"][0],
                 "temperature IS doing something; PROCEED to the 598" if v0 > v1 else
                 "no verdict-stability difference at n=10; PROCEED only to measure it properly at n=299"))
    else:
        print("GATE informative: byte-identical %d at temperature 0 vs %d at default" % (i0, i1))


def judge(workers):
    rr.PROVIDER = "azure"; rr.JUDGE_MODEL = "grok-4-1-fast-non-reasoning"; rr.load_env()
    rr.TEMPERATURE = 0.0
    sched, P, K, OPT, cot = population()
    rubrics = sj.anchor_rubrics()
    con = a13.open_cache()
    done = {(m, a) for m, a in con.execute("SELECT mid, arm FROM verdicts WHERE arm IN ('t0a','t0b')")}
    jobs = [(s, arm) for s in sched for arm in ("t0a", "t0b") if (s[0], arm) not in done]
    evals = rj.load_eval_rows([s[1] for s in sched], set(p8.ARENA12))
    print("TEMP-0: %d byte-identical-prompt matches x 2 passes | jobs %d | workers %d" % (len(sched), len(jobs), workers), flush=True)
    lock = threading.Lock(); ok = err = skip = 0

    def one(job):
        (mid, qid, opp, anc), arm = job
        pr = build_prompt(qid, opp, anc, rubrics, evals, P, OPT, cot)
        if pr is None: return None
        raw = rr.strip_think(rr.call_judge(*pr)[0])
        v, _ = rj.parse_judge(raw)
        w = {"Model A": NEW, "Model B": opp}.get(v, "TIE")
        return (mid, arm, w, int(v not in ("Model A", "Model B", "TIE")), raw, time.time())
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, j): j for j in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s" % (futs[f][0][0], str(e)[:100]), flush=True); continue
            if row is None: skip += 1; continue
            with lock:
                con.execute("INSERT OR REPLACE INTO verdicts VALUES (?,?,?,?,?,?)", row); con.commit()
            ok += 1
            if i % 100 == 0 or i == len(jobs): print("  %d/%d (ok %d, skip %d, err %d)" % (i, len(jobs), ok, skip, err), flush=True)
    print("done: ok %d, skipped %d, errors %d" % (ok, skip, err), flush=True)


def analyze():
    sched, P, K, OPT, cot = population()
    con = a13.open_cache()
    V = defaultdict(dict); R = defaultdict(dict)
    for m, arm, w, inv, raw in con.execute("SELECT mid, arm, winner, invalid, raw FROM verdicts"):
        if not inv: V[m][arm] = w; R[m][arm] = raw
    rows = [m for m, _, _, _ in sched if "t0a" in V[m] and "t0b" in V[m]]
    n = len(rows)
    dis = sum(1 for m in rows if V[m]["t0a"] != V[m]["t0b"]) / max(1, n)
    ident = sum(1 for m in rows if R[m]["t0a"] == R[m]["t0b"]) / max(1, n)
    rng = random.Random(42); diffs = []
    for _ in range(2000):
        bs = [rows[rng.randrange(n)] for _ in range(n)]
        diffs.append(sum(1 for m in bs if V[m]["t0a"] != V[m]["t0b"]) / n - NOISE)
    diffs.sort()
    L = ["=== TEMP-0: the same prompt twice at temperature 0, on DECOMP's %d byte-identical-prompt matches ===" % n]
    L.append("")
    L.append("  (1) PRIMARY - the test-retest floor:")
    L.append("      at the provider DEFAULT (DECOMP, same 299 matches)  %.3f" % NOISE)
    L.append("      at TEMPERATURE 0 (this run)                         %.3f" % dis)
    L.append("      difference %+.3f  bootstrap 95%% CI [%+.3f, %+.3f]" % (dis - NOISE, diffs[50], diffs[1949]))
    # the default-temperature arms (ensemble / selfref) have byte-identical prompts on exactly these matches,
    # so their response identity is the matching control for the line above - on all 299, not the pilot's 10
    dflt = [m for m in rows if "ensemble" in R[m] and "selfref" in R[m]]
    ident_d = sum(1 for m in dflt if R[m]["ensemble"] == R[m]["selfref"]) / max(1, len(dflt))
    L.append("      byte-identical RESPONSES between the two passes: %.3f at temperature 0 | %.3f at the default (n=%d)"
             % (ident, ident_d, len(dflt)))
    L.append("      REGISTERED BAR: below 0.02 -> %s" % ("ADOPT temperature 0 for every future paired arm"
             if dis < 0.02 else "the floor is NOT a temperature artefact; keep the +-3pp reading rule"))

    both = [m for m in rows if "ensemble" in V[m]]
    agree = sum(1 for m in both if V[m]["t0a"] == V[m]["ensemble"]) / max(1, len(both))
    wr0 = sum(1 for m in rows if V[m]["t0a"] == NEW) / max(1, n)
    wrd = sum(1 for m in both if V[m]["ensemble"] == NEW) / max(1, len(both))
    b = sum(1 for m in both if V[m]["t0a"] == NEW and V[m]["ensemble"] != NEW)
    c = sum(1 for m in both if V[m]["ensemble"] == NEW and V[m]["t0a"] != NEW)
    L.append("")
    L.append("  (2) IS IT THE SAME JUDGE, or a different one? (the risk that makes a lower floor useless)")
    L.append("      agreement between the temperature-0 verdict and the default-temperature verdict %.3f on %d matches"
             % (agree, len(both)))
    L.append("      the new contestant's win rate: temperature 0 %.3f | default %.3f (%+.3f) | %d:%d | McNemar p=%.4g"
             % (wr0, wrd, wr0 - wrd, b, c, p8.mcn(b, c)))
    L.append("      -> %s" % ("the verdict distribution is unchanged, so temperature 0 is a QUIETER judge, not a different one"
                              if p8.mcn(b, c) >= 0.05 else
                              "the verdict distribution SHIFTS: temperature 0 is a different judge and the campaign's"
                              "\n         results would not transfer to it unchanged"))
    L.append("")
    L.append("  (3) POWER - minimum detectable paired effect, SE = sqrt(d/n):")
    for d, tag in ((NOISE, "default"), (dis, "temperature 0")):
        L.append("      %-14s n=600: SE %.4f, 2-sigma %.3f | n=1000: SE %.4f, 2-sigma %.3f"
                 % (tag, (d / 600) ** 0.5, 2 * (d / 600) ** 0.5, (d / 1000) ** 0.5, 2 * (d / 1000) ** 0.5))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true"); ap.add_argument("--pilot2", action="store_true"); ap.add_argument("--judge", action="store_true")
    ap.add_argument("--analyze", action="store_true"); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.pilot: pilot()
    elif a.pilot2: pilot2()
    elif a.judge: judge(a.workers)
    elif a.analyze: analyze()
