"""REFFORM-CELL - REF-FORM-BY-CELL, the JUDGED stage (docs/judge_v2_program.md L7027-L7354, registered 2026-09-18 at
d2f5393, engineering note item 3). CONDITIONAL on C1 HELD in pot_ref_outcome.txt (F1 fired = this stage is never run).

  python tools/analysis/refform_cell.py --dry-run             # pool id first; DIFF / SAME sizes, control shas asserted, bill; 0 calls
  python tools/analysis/refform_cell.py --pilot 12            # 12 matches x 2 arms x 2 orders = 48 calls (REFUSED unless REFFORM_GO == the plan amendment)
  python tools/analysis/refform_cell.py --run [--workers 8]   # the schedule (same gate)
  python tools/analysis/refform_cell.py --analyze             # R3 / R4, C2 / C3; refuses a partial cache (writes *_partial.txt)
  python tools/analysis/refform_cell.py --selftest            # the analysis on SYNTHETIC caches (no DB of record, no call, no container)

ARMS (one knob). Both arms are STACK-v2 exactly as GROK-CALIB posted it (grok_calib.py / stack_judge.one(): prompt_v2
system template + ladder anchor rubric of the routed bareq512_s42 leaf + schema instruction; rj.build_user_prompt; dual
order; flip -> TIE; INVALID on parse failure; NON_TERMINATED on finish_reason length / content_filter, never a verdict;
cap 8,192; temperature OMITTED; rejudge_reference.with_reference untouched). The ONLY difference is the SOLVE_DB
rejudge_reference.set_reference reads: CONTROL = grok-reasoning (the incumbent), ARM P = grok-reasoning-pot (pot_ref.py);
where the PoT cache has no letter, arm P judges WITHOUT a reference block (q = ra[0], stack_judge L118 / PAIR-NOREF).
Control-arm payload SHAs are asserted per match, both orders, against experiment_results/judge_wiring/board/
payload_shas_python.csv before posting (the bytes GROK-CALIB posted); on SAME matches arm P's payload is asserted
byte-identical to the control's, on DIFF matches different.

SCHEDULE (from the two solve caches at zero verdict reads). Eligible key-decidable x12 MAIN QUANT4 matches (pot_ref.
population). DIFF = PoT letter differs from the incumbent's OR no PoT letter; SAME = the rest. Every DIFF match (cap
600, seed-42 subsample printed) + a SAME floor of 200 drawn with seed 42; cap 800 matches; both arms interleaved;
4 calls per match; the schedule order is a seed-42 shuffle so a --pilot prefix spans strata. Pinned in the cache's
`schedule` table at first launch (set hash in meta; a different schedule refuses the resume).

CACHE experiment_results/x12_crossdomain/refform_cell.db: `verdicts` keyed (match_id, arm) with vote1/vote2_raw/conf/
winner/flip/invalid/raw1/raw2/finish1/finish2/tok1/tok2/rid1/rid2/sha1/sha2/stratum; `schedule`; `meta` (protocol, judge,
cap, temperature, set hash, pot cache sha, script sha, started). Written once per (match, arm); content_filter cached
as unusable (rule 10); HTTP errors never cached.

READOUTS (--analyze, both conventions A = TIE / INVALID / NON_TERMINATED wrong and B = committed only; wrong(established)
by systematic_budget.mcnemar_edge on the cell's judged questions). R3: A and B per cell and pooled under the DEPLOYMENT
reading (cell aggregate A_P - A_C = sum over DIFF of (P - C) / kd_eligible(cell)) and the FALLBACK reading (no-yield
matches take the control verdict; post hoc, flagged, never an arm); the DIFF split fixed / broken / both-wrong-different /
no-yield with arm P minus control and a question-clustered bootstrap CI (B = 1,000, seed 42); the SAME-floor discordance;
the control-vs-GROK-CALIB discordance on the same matches (the session floor, also as sqrt(d / N) on the deciding set);
wrong(established) per cell per arm; the CONSENSUS-FIT KEY / REF logistic on arm P beside the control; per-contestant
agreement. R4: gains by TOPIC-DIFFICULTY tercile (roster difficulty, terciles within the anchor over GROK-CALIB's judged
questions). C2 / C3 and every prediction scored HELD / FAILED; Engineering descriptive; a cell < 120 kd questions UNDETERMINED.
"""
import os, sys, csv, json, math, time, random, hashlib, sqlite3, argparse, threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import numpy as np
import pool_guard
import rejudge_grok as rj
import rejudge_reasoning as rr
import rejudge_reference as rref
import rubric_p8 as p8
import stack_judge as sj
import systematic_budget as sb
import consensus_fit as cf
import pot_ref

POOL = pool_guard.MMLU_PRO_POOL
JUDGE = "grok-4-1-fast-non-reasoning"; PROVIDER = "azure"; MAXTOK = 8192
ARMS = ("control", "pot"); REFDB = {"control": "grok-reasoning", "pot": "grok-reasoning-pot"}
SAME_FLOOR = 200; DIFF_CAP = 600; CAP = 800; SEED = 42; BOOT = 1000; GUARD = 0.05; MIN_Q = 120
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refform_cell.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "refform_cell_outcome.txt")
SHAS = os.path.join(ROOT, "experiment_results", "judge_wiring", "board", "payload_shas_python.csv")
QUANT4 = pot_ref.QUANT4; CELLS_READ = pot_ref.CELLS_READ
NONTERM = ("length", "content_filter")
sj.PROMPT = "v2"


def ro(p): return sqlite3.connect("file:%s?mode=ro" % p, uri=True)
def sha_hex(b): return hashlib.sha256(b).hexdigest()
def script_sha(): return hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]
def file_sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def protocol():
    return ("STACK-v2 on %s/%s, both arms: prompt_v2 system template + ladder anchor rubric (routed leaf in bareq512_s42) + schema instruction; "
            "question block carries the arm's reference (control grok-reasoning.db, arm P grok-reasoning-pot.db; no block where arm P has no letter); "
            "dual order, flip -> TIE, INVALID if either order unparsed, NON_TERMINATED on finish length/content_filter; temperature omitted; max_tokens %d" % (PROVIDER, JUDGE, MAXTOK))


# ── the schedule ──
def references():
    out = {}
    for arm in ARMS:
        rref.set_reference(REFDB[arm])
        out[arm] = rref.references() if os.path.exists(rref.SOLVE_DB) else None
    rref.set_reference("grok-reasoning")
    return out


def pot_complete(elig):
    if not os.path.exists(pot_ref.CACHE): return False, 0
    c = ro(pot_ref.CACHE); have = {q for (q,) in c.execute("SELECT question_id FROM answers")}; c.close()
    return set(elig) <= have, len(set(elig) & have)


def substratum(r, INC, POT):
    q = r["q"]
    if q not in POT: return "no_yield"
    ic, pc = bool(INC[q][2]), bool(POT[q][2])
    if not ic and pc: return "fixed"
    if ic and not pc: return "broken"
    return "both_wrong_different" if POT[q][0] != INC[q][0] else "same"


def build_schedule(es, INC, POT, L):
    """es = eligible kd matches (pot_ref.population dicts). Returns (rows, diff_all, same_all); rows carry stratum / sub."""
    for r in es:
        assert INC[r["q"]][0] == r["ref_letter"], "match %d: incumbent letter %r != GROK-CALIB's %r" % (r["mid"], INC[r["q"]][0], r["ref_letter"])
    diff = [r for r in es if substratum(r, INC, POT) != "same"]; same = [r for r in es if substratum(r, INC, POT) == "same"]
    diff.sort(key=lambda r: r["mid"]); same.sort(key=lambda r: r["mid"])
    dj = diff
    if len(diff) > DIFF_CAP:
        dj = sorted(random.Random(SEED).sample(diff, DIFF_CAP), key=lambda r: r["mid"])
        L.append("  DIFF %d > cap %d: subsampled to %d with seed %d" % (len(diff), DIFF_CAP, DIFF_CAP, SEED))
    sj_ = sorted(random.Random(SEED).sample(same, min(SAME_FLOOR, len(same))), key=lambda r: r["mid"])
    rows = [dict(r, stratum="DIFF", sub=substratum(r, INC, POT)) for r in dj] + [dict(r, stratum="SAME", sub="same") for r in sj_]
    random.Random(SEED).shuffle(rows)
    assert len(rows) <= CAP
    return rows, diff, same


def sched_hash(rows): return hashlib.sha256(",".join("%d:%s" % (r["mid"], r["stratum"]) for r in sorted(rows, key=lambda r: r["mid"])).encode()).hexdigest()[:16]


class Assembler:
    def __init__(self, rows, refs):
        self.refs = refs; self.rubrics = sj.anchor_rubrics(); self.anchors = sj.routed_anchor()
        self.evals = rj.load_eval_rows([r["q"] for r in rows], {r["a"] for r in rows} | {r["b"] for r in rows})
        self.shas = {int(r["match_id"]): (r["sha_order1"], r["sha_order2"]) for r in csv.DictReader(open(SHAS, newline="", encoding="utf-8"))}
        assert rr.TEMPERATURE is None and rr.JUDGE_MODEL == JUDGE and rr.MAX_TOKENS == MAXTOK and rr.PROVIDER == PROVIDER
        src = open(rr.__file__, encoding="utf-8").read()
        assert "body = payload_bytes(system, user)" in src and 'return json.dumps(payload_body(system, user)).encode("utf-8")' in src

    def payload(self, r, arm):
        ra, rb = self.evals[(r["q"], r["a"])], self.evals[(r["q"], r["b"])]
        anc = self.anchors[r["q"]]; assert anc == r["anchor"], "match %d anchor %r != %r" % (r["mid"], anc, r["anchor"])
        ref = self.refs[arm].get(r["q"])
        q = rref.with_reference(ra[0], ref) if ref is not None else ra[0]
        ta, tb = rj.robust_trace(ra[2], ra[3], ra[1]), rj.robust_trace(rb[2], rb[3], rb[1])
        system = sj.system_for(anc, self.rubrics); u1, u2 = rj.build_user_prompt(q, ta, tb), rj.build_user_prompt(q, tb, ta)
        s1, s2 = sha_hex(rr.payload_bytes(system, u1)), sha_hex(rr.payload_bytes(system, u2))
        if arm == "control":
            assert (s1, s2) == self.shas[r["mid"]], "match %d: control payload sha differs from payload_shas_python.csv" % r["mid"]
        return system, u1, u2, ref, s1, s2


def configure_rr():
    rr.PROVIDER = PROVIDER; rr.JUDGE_MODEL = JUDGE; rr.MAX_TOKENS = MAXTOK; rr.TEMPERATURE = None


COLS = ["match_id", "arm", "model_a", "model_b", "qid", "anchor", "stratum", "sub", "ref_letter", "ref_correct", "vote1", "vote2_raw", "conf1", "conf2",
        "winner", "flip", "invalid", "raw1", "raw2", "finish1", "finish2", "tok1", "tok2", "rid1", "rid2", "sha1", "sha2", "ts"]


def open_cache():
    con = sqlite3.connect(CACHE)
    con.execute("CREATE TABLE IF NOT EXISTS verdicts (match_id INTEGER, arm TEXT, model_a TEXT, model_b TEXT, qid INTEGER, anchor TEXT, stratum TEXT, sub TEXT, "
                "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, raw1 TEXT, raw2 TEXT, "
                "finish1 TEXT, finish2 TEXT, tok1 INTEGER, tok2 INTEGER, rid1 TEXT, rid2 TEXT, sha1 TEXT, sha2 TEXT, ts REAL, PRIMARY KEY (match_id, arm))")
    con.execute("CREATE TABLE IF NOT EXISTS schedule (match_id INTEGER PRIMARY KEY, stratum TEXT, sub TEXT, qid INTEGER, anchor TEXT, model_a TEXT, model_b TEXT, key_winner TEXT, pos INTEGER)")
    con.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"); con.commit()
    return con


def pin_meta(con, rows):
    want = {"protocol": protocol(), "judge": JUDGE, "max_tokens": str(MAXTOK), "temperature": "omitted (provider default; Amendment 1 D2)", "schedule_hash": sched_hash(rows),
            "pot_cache_sha": file_sha(pot_ref.CACHE), "pool": POOL}
    meta = dict(con.execute("SELECT key, value FROM meta")); now = time.strftime("%Y-%m-%d %H:%M:%S")
    if not meta:
        con.executemany("INSERT INTO meta VALUES (?, ?)", list(want.items()) + [("script_sha256_16", script_sha()), ("started", now)])
        con.executemany("INSERT INTO schedule VALUES (?,?,?,?,?,?,?,?,?)", [(r["mid"], r["stratum"], r["sub"], r["q"], r["anchor"], r["a"], r["b"], r["key"], i) for i, r in enumerate(rows)])
        con.commit(); return
    bad = [(k, meta.get(k), v) for k, v in want.items() if meta.get(k) != v]
    for k, h, w in bad: print("[META] %s differs from the cache of record:\n   cached: %r\n   now:    %r" % (k, h, w))
    if bad: raise SystemExit("resume refused: a different protocol / schedule / PoT cache is a new session and gets a new cache")
    con.execute("INSERT OR REPLACE INTO meta VALUES ('resumed', ?)", ((meta.get("resumed") + ", " if meta.get("resumed") else "") + now,)); con.commit()


def c1_held():
    p = pot_ref.OUT
    if not os.path.exists(p): return False, "pot_ref_outcome.txt absent (solve stage incomplete)"
    for line in open(p, encoding="utf-8"):
        if line.strip().startswith("C1 "): return line.strip().endswith("HELD"), line.strip()
    return False, "no C1 line in pot_ref_outcome.txt"


def setup(L):
    L.append("[POOL] %s (pool of record; pool_guard.assert_pool_of_record passed)" % POOL)
    kd, META, K, P, elig = pot_ref.population(); es = [r for r in kd if r["q"] in set(elig)]
    ok, n = pot_complete(elig)
    L.append("[SOLVE-STAGE] %s: %d of %d eligible questions cached%s" % (os.path.basename(pot_ref.CACHE), n, len(elig), "" if ok else " -> INCOMPLETE: DIFF / SAME sizes unknown, no schedule"))
    held, line = c1_held(); L.append("[C1] %s -> judged stage %s" % (line, "authorised by the registration" if held else "NOT authorised (conditional on C1 HELD)"))
    refs = references(); INC = refs["control"]; POT = refs["pot"] or {}
    return kd, META, K, P, elig, es, ok, held, INC, POT, refs


def dry_run():
    L = []; kd, META, K, P, elig, es, ok, held, INC, POT, refs = setup(L)
    L.append("[RUN]  REF-FORM-BY-CELL judged stage | judge %s on %s | max_tokens %d | temperature omitted | arms %s -> %s" % (JUDGE, PROVIDER, MAXTOK, ARMS, REFDB))
    L.append("[ELIGIBLE] %d kd matches on %d questions (per cell q: %s)" % (len(es), len(elig), ", ".join("%s %d" % (a, len({r["q"] for r in es if r["anchor"] == a})) for a in QUANT4)))
    L.append("[BILL BOUNDS] DIFF (<= %d) + SAME floor %d, cap %d matches x 2 arms x 2 orders = <= %d calls" % (DIFF_CAP, SAME_FLOOR, CAP, 4 * CAP))
    if not ok:
        # the solve cache does not exist yet: prove the CONTROL arm over the whole eligible population at zero calls
        # (every payload assembled, sha asserted against payload_shas_python.csv, both orders), and the arm P no-reference form differs
        configure_rr(); asm = Assembler(es, {"control": INC, "pot": {}}); nb = 0; differ = 0
        for r in es:
            sc = asm.payload(r, "control"); sp = asm.payload(r, "pot"); nb += len(sc[1]) + len(sc[2]); differ += (sc[4], sc[5]) != (sp[4], sp[5])
        L.append("[DRY-RUN] control arm: %d eligible kd matches x 2 orders assembled (%.1f MB), sha == payload_shas_python.csv on all %d | arm P no-reference form differs on %d"
                 % (len(es), nb / 1e6, len(es), differ))
        L.append("[DRY-RUN] solve stage incomplete: schedule not built; 0 calls made, no file created"); print("\n".join(L)); return
    rows, diff, same = build_schedule(es, INC, POT, L)
    sub = Counter(substratum(r, INC, POT) for r in diff)
    L.append("[STRATA] DIFF %d matches / %d q (%s) | SAME %d / %d q | judged: DIFF %d + SAME %d = %d matches | schedule hash %s"
             % (len(diff), len({r["q"] for r in diff}), ", ".join("%s %d" % kv for kv in sorted(sub.items())), len(same), len({r["q"] for r in same}),
                sum(1 for r in rows if r["stratum"] == "DIFF"), sum(1 for r in rows if r["stratum"] == "SAME"), len(rows), sched_hash(rows)))
    L.append("[BILL] %d matches x 2 arms x 2 orders = %d calls (%d cached (match, arm) rows)" % (len(rows), 4 * len(rows), len(cached_keys())))
    configure_rr(); asm = Assembler(rows, refs); nb = 0; same_ident = diff_differ = 0
    for r in rows:
        sc = asm.payload(r, "control"); sp = asm.payload(r, "pot"); nb += sum(len(x.encode()) for x in (sc[0], sc[1], sc[2], sp[0], sp[1], sp[2]))
        if r["stratum"] == "SAME": assert (sc[4], sc[5]) == (sp[4], sp[5]), "SAME match %d: arm P payload differs" % r["mid"]; same_ident += 1
        else: assert (sc[4], sc[5]) != (sp[4], sp[5]), "DIFF match %d: arm P payload identical to control" % r["mid"]; diff_differ += 1
    L.append("[DRY-RUN] %d payloads assembled (%.1f MB) | control shas == payload_shas_python.csv on all %d matches | SAME byte-identical %d | DIFF differ %d | nothing posted"
             % (4 * len(rows), nb / 1e6, len(rows), same_ident, diff_differ))
    r = rows[0]; sc = asm.payload(r, "control"); sp = asm.payload(r, "pot")
    L.append("[FIRST] match %d | %s vs %s | q %d | %s | %s/%s | control ref %s | arm P ref %s" % (r["mid"], r["a"], r["b"], r["q"], r["anchor"], r["stratum"], r["sub"], sc[3][0], sp[3][0] if sp[3] else "(none)"))
    L.append("[DRY-RUN] OK: 0 calls made, no file created"); print("\n".join(L))


def cached_keys():
    if not os.path.exists(CACHE): return set()
    c = ro(CACHE); s = {(m, a) for m, a in c.execute("SELECT match_id, arm FROM verdicts")}; c.close(); return s


def run(pilot, workers):
    L = []; kd, META, K, P, elig, es, ok, held, INC, POT, refs = setup(L); print("\n".join(L))
    pot_ref.go_gate("--pilot" if pilot else "--run")
    if not ok: raise SystemExit("[RUN] solve stage incomplete: refused")
    if not held: raise SystemExit("[RUN] C1 not HELD in pot_ref_outcome.txt: the judged stage is conditional on C1 (F1 fired -> not run)")
    rows, diff, same = build_schedule(es, INC, POT, L)
    configure_rr(); rr.load_env(); con = open_cache(); pin_meta(con, rows)
    done = {(m, a) for m, a in con.execute("SELECT match_id, arm FROM verdicts")}
    sched = rows[:pilot] if pilot else rows
    jobs = [(r, arm) for r in sched for arm in ARMS if (r["mid"], arm) not in done]
    print("[RUN] schedule %d matches (%s) | cached %d rows | posting %d (match, arm) jobs = %d calls | workers %d" % (len(sched), "pilot" if pilot else "run", len(done), len(jobs), 2 * len(jobs), workers), flush=True)
    asm = Assembler(sched, refs); lock = threading.Lock(); okc = err = 0

    def one(r, arm):
        system, u1, u2, ref, s1, s2 = asm.payload(r, arm)
        c1, p1, k1, l1, f1, m1 = rr.call_judge_full(system, u1); c2, p2, k2, l2, f2, m2 = rr.call_judge_full(system, u2)
        raw1, raw2 = rr.strip_think(c1), rr.strip_think(c2)
        v1, cf1 = rj.parse_judge(raw1); v2, cf2 = rj.parse_judge(raw2)
        w, flip, inv = rj.combine_orders(v1, v2)
        return (r["mid"], arm, r["a"], r["b"], r["q"], r["anchor"], r["stratum"], r["sub"], ref[0] if ref else "", int(ref[2]) if ref else -1, v1, v2, cf1, cf2,
                {"Model A": r["a"], "Model B": r["b"]}.get(w, w), int(flip), int(inv), raw1, raw2, f1, f2, k1, k2,
                (m1 or {}).get("_response_id"), (m2 or {}).get("_response_id"), s1, s2, time.time())
    ins = "INSERT OR IGNORE INTO verdicts (%s) VALUES (%s)" % (",".join(COLS), ",".join("?" * len(COLS)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, r, arm): (r["mid"], arm) for r, arm in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            try: row = f.result()
            except Exception as e:
                err += 1; print("  ERROR %s: %s (not cached)" % (futs[f], str(e)[:140]), flush=True); continue
            with lock: con.execute(ins, row); con.commit()
            okc += 1
            if i % 25 == 0 or i == len(jobs): print("  %d/%d (ok %d, err %d)" % (i, len(jobs), okc, err), flush=True)
    print("done: ok %d, errors %d" % (okc, err), flush=True)
    analyze(pilot=pilot)


# ── analysis core (data in, lines out; the selftest feeds synthetic data) ──
def acc_conv(v, key, conv):
    """1 / 0 / None: correct under the convention; None = excluded from B's denominator."""
    if v is None: return 0 if conv == "A" else None
    w = v["winner"]; nt = v.get("finish1") in NONTERM or v.get("finish2") in NONTERM
    if v["invalid"] or nt or w in ("TIE", "INVALID"): return 0 if conv == "A" else None
    return int(w == key)


def mean_ci(vals, qids, B=BOOT, seed=SEED):
    """mean and a question-clustered bootstrap percentile CI of a per-match statistic."""
    if not vals: return float("nan"), (float("nan"), float("nan"))
    byq = defaultdict(list)
    for v, q in zip(vals, qids): byq[q].append(v)
    qs = sorted(byq); rng = np.random.default_rng(seed); ms = []
    for _ in range(B):
        pick = rng.integers(0, len(qs), len(qs)); s = [x for i in pick for x in byq[qs[i]]]; ms.append(sum(s) / len(s))
    return sum(vals) / len(vals), (float(np.percentile(ms, 2.5)), float(np.percentile(ms, 97.5)))


def analyze_core(sched, V, calib, K, P, es_all, tercile, L, pilot=False):
    """sched: list of schedule dicts (mid, stratum, sub, q, anchor, a, b, key); V: {(mid, arm): verdict dict(winner, invalid, finish1, finish2, ref_letter)};
    calib: {mid: verdict dict} GROK-CALIB's cached control; es_all: every eligible kd match dict (mid, q, anchor, a, b, key) with 'calib' verdict; tercile: q -> tercile."""
    missing = [(r["mid"], a) for r in sched for a in ARMS if (r["mid"], a) not in V]
    n_sched = len(sched); by_mid = {r["mid"]: r for r in sched}
    # truncation guard on the deciding subset (every scheduled match is key-decidable), per arm
    L.append("  GUARD (refuse above %.0f%% unparsed on the deciding subset = scheduled kd matches, per arm):" % (100 * GUARD)); refuse = False
    for arm in ARMS:
        un = sum(1 for r in sched if (r["mid"], arm) not in V or V[(r["mid"], arm)]["invalid"] or V[(r["mid"], arm)].get("finish1") in NONTERM or V[(r["mid"], arm)].get("finish2") in NONTERM)
        rate = un / max(1, n_sched); refuse |= rate > GUARD
        L.append("     %-8s unparsed / missing %d of %d = %.1f%% [%s]" % (arm, un, n_sched, 100 * rate, "OK" if rate <= GUARD else "REFUSED"))
    if refuse: L.append("  C3 UNDETERMINED: the guard refuses the deciding set");
    diff_rows = [r for r in sched if r["stratum"] == "DIFF"]; same_rows = [r for r in sched if r["stratum"] == "SAME"]
    diff_all = [r for r in es_all if r["sub"] != "same"]; scale = len(diff_all) / max(1, len(diff_rows))
    kd_cell = Counter(r["anchor"] for r in es_all); kd_q = {a: len({r["q"] for r in es_all if r["anchor"] == a}) for a in QUANT4}
    if not diff_rows: L.append("  no DIFF matches judged"); return {}
    # per-match arm P minus control on judged DIFF, both conventions (B: only matches committed in BOTH arms)
    def d_match(r, conv, fallback=False):
        c = acc_conv(V.get((r["mid"], "control")), r["key"], conv); p = acc_conv(V.get((r["mid"], "pot")), r["key"], conv)
        if fallback and r["sub"] == "no_yield": p = c
        return None if (c is None or p is None) else p - c
    res = {}
    L.append("")
    L.append("(R3) JUDGED. Cell aggregate A_P - A_C = sum over DIFF of (P - C) / kd_eligible(cell)%s; SAME contributes its measured discordance as the floor.%s"
             % (" x %.2f (DIFF subsampled)" % scale if scale > 1 else "", "  [PILOT: a prefix of the schedule, the aggregate is a guard readout, not a reading]" if pilot else ""))
    L.append("  %-12s %5s %5s | %-34s | %-34s | %s" % ("cell", "kd_m", "kd_q", "DEPLOYMENT gain A [CI]   B", "FALLBACK gain A [CI]     B", "status"))
    for anc in QUANT4 + ("QUANT4",):
        rs = [r for r in diff_rows if anc == "QUANT4" or r["anchor"] == anc]; N = kd_cell[anc] if anc != "QUANT4" else sum(kd_cell.values()); Nq = kd_q[anc] if anc != "QUANT4" else sum(kd_q.values())
        out = {}
        for fb in (False, True):
            for conv in ("A", "B"):
                d = [(d_match(r, conv, fb), r["q"]) for r in rs]; d = [(x, q) for x, q in d if x is not None]
                m, (lo, hi) = mean_ci([x for x, _ in d], [q for _, q in d]) if d else (0.0, (0.0, 0.0))
                f = len(d) * scale / max(1, N)                # judged DIFF matches -> share of the cell's eligible kd matches
                out[(fb, conv)] = (m * f, lo * f, hi * f, len(d))
        res[anc] = out
        status = "descriptive (UNDETERMINED-by-support, %d q < %d)" % (Nq, MIN_Q) if (anc != "QUANT4" and (anc not in CELLS_READ or Nq < MIN_Q)) else "read"
        L.append("  %-12s %5d %5d | %+6.2fpp [%+6.2f, %+6.2f] %+6.2fpp | %+6.2fpp [%+6.2f, %+6.2f] %+6.2fpp | %s (n DIFF judged A %d / B %d)"
                 % (anc, N, Nq, 100 * out[(False, "A")][0], 100 * out[(False, "A")][1], 100 * out[(False, "A")][2], 100 * out[(False, "B")][0],
                    100 * out[(True, "A")][0], 100 * out[(True, "A")][1], 100 * out[(True, "A")][2], 100 * out[(True, "B")][0], status, out[(False, "A")][3], out[(False, "B")][3]))
    # DIFF split
    L.append("")
    L.append("  DIFF split (arm P minus control per judged match, question-clustered bootstrap B=%d seed %d):" % (BOOT, SEED))
    split = {}
    for sub_ in ("fixed", "broken", "both_wrong_different", "no_yield"):
        rs = [r for r in diff_rows if r["sub"] == sub_]
        if not rs: L.append("     %-22s n 0" % sub_); continue
        dA = [(d_match(r, "A"), r["q"]) for r in rs]; dB = [(d_match(r, "B"), r["q"]) for r in rs]; dB = [(x, q) for x, q in dB if x is not None]
        mA, ciA = mean_ci([x for x, _ in dA], [q for _, q in dA]); mB, ciB = mean_ci([x for x, _ in dB], [q for _, q in dB]) if dB else (float("nan"), (float("nan"), float("nan")))
        accC = sum(acc_conv(V.get((r["mid"], "control")), r["key"], "A") for r in rs) / len(rs); accP = sum(acc_conv(V.get((r["mid"], "pot")), r["key"], "A") for r in rs) / len(rs)
        split[sub_] = dict(n=len(rs), q=len({r["q"] for r in rs}), mA=mA, ciA=ciA, mB=mB, ciB=ciB, accC=accC, accP=accP)
        L.append("     %-22s n %4d / %3d q | control A %.3f -> arm P %.3f | P - C: A %+.3f [%+.3f, %+.3f] | B %+.3f [%+.3f, %+.3f] (n %d)"
                 % (sub_, len(rs), len({r["q"] for r in rs}), accC, accP, mA, ciA[0], ciA[1], mB, ciB[0], ciB[1], len(dB)))
    # floors
    def disc(pairs):
        n = sum(1 for a, b in pairs if a is not None and b is not None); d = sum(1 for a, b in pairs if a is not None and b is not None and a["winner"] != b["winner"])
        return d / max(1, n), d, n
    sd, sdn, sdd = disc([(V.get((r["mid"], "control")), V.get((r["mid"], "pot"))) for r in same_rows])
    cd, cdn, cdd = disc([(V.get((r["mid"], "control")), calib.get(r["mid"])) for r in sched])
    Ndec = sum(kd_cell.values()); floor = math.sqrt(cd / max(1, Ndec))
    accC_s = sum(acc_conv(V.get((r["mid"], "control")), r["key"], "A") for r in sched) / max(1, n_sched); accK_s = sum(acc_conv(calib.get(r["mid"]), r["key"], "A") for r in sched) / max(1, n_sched)
    L.append("")
    L.append("  FLOORS: SAME-stratum discordance (control vs arm P, byte-identical prompts) %d of %d = %.1f%% | control-vs-GROK-CALIB discordance on the %d judged matches %d of %d = %.1f%% "
             "(control A %.3f vs cache A %.3f, |delta| %.1fpp) | session floor sqrt(d / N_deciding=%d) = %.2fpp" % (sdn, sdd, 100 * sd, n_sched, cdn, cdd, 100 * cd, accC_s, accK_s, 100 * abs(accC_s - accK_s), Ndec, 100 * floor))
    # C2 / C3
    fx, bk = split.get("fixed"), split.get("broken")
    c2 = bool(fx and bk and fx["mA"] >= 0.40 and fx["ciA"][0] > 0 and bk["mA"] <= -0.40 and bk["ciA"][1] < 0)
    L.append("")
    L.append("  C2 (the judge transcribes it): fixed P - C A %s (bar >= +0.40, CI excl. 0) | broken %s (bar <= -0.40, CI excl. 0) -> %s%s"
             % ("%+.3f [%+.3f, %+.3f]" % (fx["mA"], *fx["ciA"]) if fx else "n/a", "%+.3f [%+.3f, %+.3f]" % (bk["mA"], *bk["ciA"]) if bk else "n/a", "HELD" if c2 else "FAILED",
                "" if (fx and bk) else " (a stratum is empty: one-sided evidence only)"))
    Q = res["QUANT4"]; gA, loA, hiA, _ = Q[(False, "A")]; gB, loB, hiB, _ = Q[(False, "B")]
    c3 = (not refuse) and gA >= floor and gA >= 0.01 and loA > 0 and gB >= floor and gB >= 0.01 and loB > 0
    L.append("  C3 (a cell gain that could ship): pooled QUANT4 deployment gain A %+.2fpp [%+.2f, %+.2f] | B %+.2fpp [%+.2f, %+.2f] | floor %.2fpp | bar >= floor and >= +1.0pp with CI excl. 0 under BOTH -> %s"
             % (100 * gA, 100 * loA, 100 * hiA, 100 * gB, 100 * loB, 100 * hiB, 100 * floor, "UNDETERMINED (guard)" if refuse else ("HELD" if c3 else "FAILED")))
    for anc in CELLS_READ:
        o = res[anc]; ga, la, ha, _ = o[(False, "A")]; gb, lb, hb, _ = o[(False, "B")]
        und = kd_q[anc] < MIN_Q
        L.append("     C3 %-10s A %+.2fpp [%+.2f, %+.2f] B %+.2fpp [%+.2f, %+.2f] -> %s" % (anc, 100 * ga, 100 * la, 100 * ha, 100 * gb, 100 * lb, 100 * hb,
                 "UNDETERMINED (%d q < %d)" % (kd_q[anc], MIN_Q) if und else ("HELD" if (ga >= floor and ga >= 0.01 and la > 0 and gb >= floor and gb >= 0.01 and lb > 0) else "FAILED")))
    # predictions
    ny = split.get("no_yield"); fbA = Q[(True, "A")][0]
    eng = res["Engineering"][(False, "A")][0] if "Engineering" in res else float("nan")
    others = [res[a][(False, "A")][0] for a in CELLS_READ if a in res]
    preds = [("fixed-match gain +0.45..+0.65", fx["mA"] if fx else float("nan"), 0.45, 0.65), ("broken-match loss -0.65..-0.45", bk["mA"] if bk else float("nan"), -0.65, -0.45),
             ("no-yield matches -0.14..-0.08", ny["mA"] if ny else float("nan"), -0.14, -0.08), ("SAME-floor discordance 4-8%", sd, 0.04, 0.08), ("control-vs-cache discordance 4-8%", cd, 0.04, 0.08),
             ("pooled deployment gain -1.5..+1.5pp (C3 FAILED expected)", gA, -0.015, 0.015), ("fallback reading +0.5..+1.5pp", fbA, 0.005, 0.015)]
    L.append("")
    L.append("  PREDICTIONS:")
    for name, v, lo, hi in preds: L.append("     %-58s %+.3f -> %s" % (name, v, "n/a" if v != v else ("HELD" if lo <= v <= hi else "FAILED")))
    L.append("     %-58s Engineering %+.2fpp, others max %+.2fpp -> %s" % ("Engineering the only cell with a point gain > +2pp", 100 * eng, 100 * max(others) if others else float("nan"),
             "HELD" if (eng > 0.02 and all(o <= 0.02 for o in others)) else "FAILED"))
    # wrong(established) per cell per arm on the population verdicts (judged DIFF from the arm; every other eligible match = the cached control draw)
    L.append("")
    L.append("  wrong(established) per cell per arm (edge direction from the arm's population verdicts vs the key; established = exact McNemar p < 0.05 on the cell's judged questions):")
    anchor_qs = {a: sorted({r["q"] for r in es_all if r["anchor"] == a}) for a in QUANT4}
    for arm in ARMS:
        parts = []
        for anc in QUANT4:
            rs = [r for r in es_all if r["anchor"] == anc]; wins = defaultdict(lambda: [0.0, 0])
            for r in rs:
                v = V.get((r["mid"], arm)) if (r["mid"] in by_mid and by_mid[r["mid"]]["stratum"] == "DIFF") else r["calib"]
                w = v["winner"] if v and not v["invalid"] else "INVALID"
                key_ = (min(r["a"], r["b"]), max(r["a"], r["b"])); s = 0.5 if w == "TIE" else (1.0 if w == key_[0] else (0.0 if w == key_[1] else None))
                if s is not None: wins[key_][0] += s; wins[key_][1] += 1
            wrong = est = 0
            for (a, b), (s, n) in wins.items():
                p, b_, c_ = sb.mcnemar_edge(dict(anchor=anc, a=a, b=b), K, anchor_qs)
                if p < 0.05 and b_ != c_:
                    est += 1; jd = (s / n) - 0.5
                    if jd != 0 and (jd > 0) != (b_ > c_): wrong += 1
            parts.append("%s %d(%d)" % (anc, wrong, est))
        L.append("     %-8s %s" % (arm, " | ".join(parts)))
    # CONSENSUS-FIT on the judged matches, arm P beside control
    L.append("")
    L.append("  CONSENSUS-FIT (match-level logistic of the verdict on the signed KEY and REF contrasts, judged matches, both strata):")
    for arm in ARMS:
        rows_ = []
        for r in sched:
            v = V.get((r["mid"], arm))
            if v is None or v["invalid"]: continue
            pa, pb = P.get(r["q"], {}).get(r["a"]), P.get(r["q"], {}).get(r["b"])
            if pa is None or pb is None: continue
            kc = cf.sign_contrast(K[r["q"]].get(r["a"], 0) == 1, K[r["q"]].get(r["b"], 0) == 1)
            rl = (v.get("ref_letter") or "").strip().upper()[:1]; rc = cf.sign_contrast(rl == pa, rl == pb) if rl else 0.0
            rows_.append((kc, rc, "A" if v["winner"] == r["a"] else ("B" if v["winner"] == r["b"] else "TIE")))
        if len(rows_) >= 20:
            try: cf.fit_matches(rows_, "arm %s" % arm, L)
            except Exception as e: L.append("     arm %s: fit failed (%s)" % (arm, e))
        else: L.append("     arm %s: %d rows, too few to fit" % (arm, len(rows_)))
    # per-contestant agreement of arm P's verdicts
    L.append("")
    L.append("  Per-contestant: judged matches with the contestant, share it wins under control vs arm P, verdict agreement P == C:")
    for m in sorted(p8.ARENA12):
        rs = [r for r in sched if m in (r["a"], r["b"]) and (r["mid"], "control") in V and (r["mid"], "pot") in V]
        if not rs: continue
        wc = sum(1 for r in rs if V[(r["mid"], "control")]["winner"] == m) / len(rs); wp = sum(1 for r in rs if V[(r["mid"], "pot")]["winner"] == m) / len(rs)
        ag = sum(1 for r in rs if V[(r["mid"], "control")]["winner"] == V[(r["mid"], "pot")]["winner"]) / len(rs)
        L.append("     %-30s n %4d | wins control %.3f -> arm P %.3f (%+.3f) | agreement %.3f%s" % (m[:30], len(rs), wc, wp, wp - wc, ag, "   <- frontier" if m in pot_ref.FRONTIER else ""))
    # R4 terciles
    L.append("")
    L.append("(R4) DESCRIPTIVE: deployment gain (A) by TOPIC-DIFFICULTY tercile (roster difficulty, terciles within the anchor over GROK-CALIB's judged questions), pooled QUANT4:")
    for t in ("hard", "mid", "easy"):
        rs = [r for r in diff_rows if tercile.get(r["q"]) == t]; N = sum(1 for r in es_all if tercile.get(r["q"]) == t)
        d = [(d_match(r, "A"), r["q"]) for r in rs]
        m, (lo, hi) = mean_ci([x for x, _ in d], [q for _, q in d]) if d else (0.0, (0.0, 0.0)); f = len(d) * scale / max(1, N)
        L.append("     %-5s kd matches %4d | DIFF judged %3d | gain %+.2fpp [%+.2f, %+.2f]" % (t, N, len(rs), 100 * m * f, 100 * lo * f, 100 * hi * f))
    L.append("")
    L.append("  STATUS: %s" % ("PILOT (%d matches): no outcome of record" % n_sched if pilot else ("PARTIAL: %d (match, arm) rows missing of %d - no outcome of record" % (len(missing), 2 * n_sched) if missing else "COMPLETE - outcome of record")))
    return dict(c2=c2, c3=c3, split=split, res=res, sd=sd, cd=cd, floor=floor, missing=missing, refuse=refuse)


def load_verdicts():
    c = ro(CACHE)
    V = {(m, a): dict(winner=w, invalid=inv, finish1=f1, finish2=f2, ref_letter=rl) for m, a, w, inv, f1, f2, rl in c.execute("SELECT match_id, arm, winner, invalid, finish1, finish2, ref_letter FROM verdicts")}
    sched = [dict(mid=m, stratum=s, sub=sub, q=q, anchor=anc, a=a, b=b, key=k) for m, s, sub, q, anc, a, b, k, _ in c.execute("SELECT * FROM schedule ORDER BY pos")]
    meta = dict(c.execute("SELECT key, value FROM meta")); c.close()
    return V, sched, meta


def terciles(kd, K):
    """TOPIC-DIFFICULTY's instrument: roster difficulty, rank terciles within the anchor over GROK-CALIB's judged questions (all kd rows here carry them)."""
    gc = ro(pot_ref.CALIB_DB); byq = defaultdict(set)
    for q, anc in gc.execute("SELECT qid, anchor FROM verdicts WHERE anchor IN (?,?,?,?)", QUANT4): byq[anc].add(q)
    gc.close(); out = {}
    for anc, qs in byq.items():
        diff = {q: (sum(K[q].values()) / len(K[q])) for q in qs if K.get(q)}
        order = sorted(diff, key=lambda q: (diff[q], q)); n = len(order); b1, b2 = n // 3, (2 * n) // 3
        for i, q in enumerate(order): out[q] = "easy" if i >= b2 else ("mid" if i >= b1 else "hard")
    return out


def analyze(pilot=None):
    L = []; kd, META, K, P, elig, es, ok, held, INC, POT, refs = setup(L)
    if not os.path.exists(CACHE): L.append("[ANALYZE] no cache at %s" % CACHE); print("\n".join(L)); return
    V, sched, meta = load_verdicts()
    if pilot: sched = sched[:pilot]
    calib = {r["mid"]: dict(winner=r["winner"], invalid=r["invalid"], finish1=r["finish1"], finish2=r["finish2"]) for r in es}
    es_all = [dict(r, sub=substratum(r, INC, POT), calib=calib[r["mid"]]) for r in es]
    L.append("=== REF-FORM-BY-CELL judged stage | cache %s | schedule %d matches (hash %s, started %s) | %d (match, arm) rows ===" % (os.path.basename(CACHE), len(sched), meta.get("schedule_hash"), meta.get("started"), len(V)))
    out = analyze_core(sched, V, calib, K, P, es_all, terciles(kd, K), L, pilot=bool(pilot))
    txt = "\n".join(L); print(txt)
    complete = bool(out) and not out["missing"] and not pilot
    path = OUT if complete else OUT.replace("outcome", "PILOT" if pilot else "partial")
    open(path, "w", encoding="utf-8").write(txt + "\n"); print("[ANALYZE] -> %s%s" % (path, "" if complete else "  (REFUSED as the outcome of record: partial / pilot)"))


# ── selftest on synthetic caches ──
def selftest():
    rng = random.Random(7); models = sorted(p8.ARENA12); L = []
    K = defaultdict(dict); P = defaultdict(dict); es_all = []; sched = []; V = {}; calib = {}; tercile = {}; mid = 0; q = 0
    subs = ["same"] * 20 + ["fixed"] * 5 + ["broken"] * 3 + ["both_wrong_different"] * 2 + ["no_yield"] * 4
    for anc in QUANT4:
        for i in range(70):
            q += 1; tercile[q] = ("hard", "mid", "easy")[i % 3]; sub = subs[i % len(subs)]
            for m in models: K[q][m] = rng.randint(0, 1); P[q][m] = "ABCD"[rng.randint(0, 3)]
            for _ in range(2):
                a, b = rng.sample(models, 2)
                if K[q][a] == K[q][b]: K[q][b] = 1 - K[q][a]
                key = a if K[q][a] else b; wrong = b if key == a else a; mid += 1
                ref_c_right = sub in ("same", "broken"); pot_right = sub in ("same", "fixed")
                def verdict(right, tie=0.06):
                    u = rng.random()
                    if u < tie: return "TIE"
                    return key if rng.random() < (0.9 if right else 0.3) else wrong
                cw = verdict(ref_c_right); kw = cw if rng.random() > 0.05 else verdict(ref_c_right)
                cal = dict(winner=kw, invalid=0, finish1="stop", finish2="stop")
                r = dict(mid=mid, q=q, anchor=anc, a=a, b=b, key=key, sub=sub, calib=cal, ref_letter="A", ref_correct=int(ref_c_right)); es_all.append(r); calib[mid] = cal
                if sub != "same" or (i % 7 == 0):
                    sched.append(dict(mid=mid, stratum="DIFF" if sub != "same" else "SAME", sub=sub, q=q, anchor=anc, a=a, b=b, key=key))
                    V[(mid, "control")] = dict(winner=cw, invalid=0, finish1="stop", finish2="stop", ref_letter=P[q][key] if ref_c_right else P[q][wrong])
                    pw = (cw if rng.random() > 0.05 else verdict(True)) if sub == "same" else (verdict(False, 0.15) if sub == "no_yield" else verdict(pot_right))
                    V[(mid, "pot")] = dict(winner=pw, invalid=0, finish1="stop", finish2="stop", ref_letter=(P[q][key] if pot_right else P[q][wrong]) if sub != "no_yield" else "")
    out = analyze_core(sched, V, calib, K, P, es_all, tercile, L)
    txt = "\n".join(L); print(txt)
    fx, bk = out["split"]["fixed"], out["split"]["broken"]
    assert fx["mA"] > 0.4 and fx["ciA"][0] > 0, fx
    assert bk["mA"] < -0.4 and bk["ciA"][1] < 0, bk
    assert out["c2"] and not out["refuse"] and not out["missing"]
    assert 0.0 <= out["sd"] <= 0.2 and 0.0 <= out["cd"] <= 0.2
    assert "wrong(established)" in txt and "CONSENSUS-FIT" in txt and "(R4)" in txt and "C3" in txt
    # a partial cache is refused as the outcome of record
    V2 = dict(V); V2.pop((sched[0]["mid"], "pot")); L2 = []; out2 = analyze_core(sched, V2, calib, K, P, es_all, tercile, L2)
    assert out2["missing"] == [(sched[0]["mid"], "pot")] and "PARTIAL" in "\n".join(L2)
    # the guard refuses when > 5% are non-terminated
    V3 = dict(V)
    for k in list(V3)[: int(0.08 * len(V3))]: V3[k] = dict(V3[k], finish1="length", invalid=1)
    L3 = []; out3 = analyze_core(sched, V3, calib, K, P, es_all, tercile, L3); assert out3["refuse"] and "UNDETERMINED (guard)" in "\n".join(L3)
    print("[REFFORM-CELL] selftest PASS: synthetic fixed %+.3f [%+.3f, %+.3f], broken %+.3f [%+.3f, %+.3f], C2 %s; partial cache refused; guard refusal exercised"
          % (fx["mA"], *fx["ciA"], bk["mA"], *bk["ciA"], "HELD" if out["c2"] else "FAILED"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--pilot", type=int, default=None); ap.add_argument("--run", action="store_true")
    ap.add_argument("--analyze", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    pool_guard.assert_pool_of_record(POOL)
    if a.dry_run: dry_run()
    elif a.analyze: analyze(pilot=a.pilot)
    elif a.pilot or a.run: run(a.pilot, a.workers)
    else: ap.print_help()
