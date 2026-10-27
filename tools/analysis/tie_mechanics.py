"""TIE-MECHANICS — is the canary's "every retest disagreement sits at the tie boundary, and no decisive match reverses" a property of
the judge, or the arithmetic that independent per-call vote changes force through the dual-order TIE-on-flip rule? (zero calls; a
CONSISTENCY CHECK on the two CANARY-BASELINE caches)

REGISTRATION OF RECORD: docs/judge_v2_program.md L12911-L13030 (commit 3c2fcab), heading "## Registered 2026-09-23 (before any code or
call) — TIE-MECHANICS: ..."; record docs/agents/results/TIE-MECHANICS.json. Zero judge calls; reads NO key, NO reference, NO prompt.

LAUNCH SEQUENCE:
  python tools/analysis/tie_mechanics.py --selftest     (synthetic cache pairs of KNOWN dependence under tempfile.mkdtemp(); both C1
                                                          branches executed; every criterion / prediction / falsifier print branch executed)
  python tools/analysis/tie_mechanics.py --dry-run      (zero calls, writes nothing: pool id, set hash, both caches' row counts and schemas,
                                                          the R1 counts; exits)
  python tools/analysis/tie_mechanics.py --run          (writes experiment_results/x12_crossdomain/tie_mechanics_outcome.txt WRITE-ONCE,
                                                          mode "x"; refuses if it exists; a failed refusal gate writes nothing)

HYGIENE (the registration's). First printed line on every mode: pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL). The set of
record experiment_results/x12_crossdomain/canary_set.json is re-hashed with set_hash() — a local copy asserted AST-identical to
canary_baseline.set_hash, never an import (canary_baseline imports stack_judge, whose open_cache() opens READ-WRITE) — against
50af669ac6997f9f, and each cache's (match_id, qid, model_a, model_b, stratum) set must equal the set's. Both caches are opened
mode=ro&immutable=1 through vote_frame_cert.open_ro (URI flags asserted, PRAGMA query_only=1 read back); size and mtime (and any -wal /
-shm) printed before and after and asserted unchanged; pass 1's sha256 asserted equal to 5142795bdc8c5a8ec8d09a3a4f9cd6c84de206834aeab7ca11cea4761000690c
(the pass-2 READY); 300 rows and 300 distinct match ids in each, asserted.
THE FRAME (the registration: a row-level reproduction is this test's frame certificate): every stored winner must equal the canary's
own aggregation name_of(rejudge_grok.combine_orders(vote1, vote2_raw)) (canary_baseline.py L432-L437, a length finish forcing INVALID) on
every row of both caches, and the two schemas must be identical on every column the aggregation reads.
[DEVIATION FORCED BY THE RECORD, reported to the registrar: the registration asks that "the two schemas are identical"; canary_baseline.py's
docstring bracket [ADDED 2026-09-22] records that pass 1 predates the provider1 / provider2 columns ("a cache without the columns (pass 1)
... is never migrated"), so a literal whole-schema equality would refuse the pair of record. The instrument asserts identity on every
column except exactly {provider1, provider2}, prints the full difference, and refuses on any other.]
[RULED 2026-09-23 by the registrar, ruling (1), programme L13691-L13746 (04379d7): CONFIRMED as identity of every column NAME, TYPE and
ORDER except exactly {provider1, provider2}, which may be ABSENT FROM PASS 1 ONLY; any other difference refuses under gate R1; the excluded
columns are printed. schema_check() below implements exactly that (ordered lists of (name, declared type), not sets).]
[CORRECTED 2026-09-23 by the READY review docs/reviews/NOT_READY_vote_frame_family.md (14edeb4), T-C1 / T-C2 / L2: open_ro's guards are explicit
raises (T-C1, in vote_frame_cert.open_ro); the pool guard is injectable and the selftest EXECUTES it, and the pass-1 sha256 refusal, on
both branches (T-C2); the schema compared is that of the `verdicts` table, the table the registration's counts read (run_meta is not
compared, and the [SCHEMA] line says so) (L2).]

REFUSAL GATES (a failed gate writes no outcome; gates are not verdict clauses). R1 the recorded counts reproduced exactly: 26 verdict
changes (16 TIE -> decisive, 10 decisive -> TIE), 215 decisive in both passes, 0 direct reversals, 59 of 600 changed order votes, 23
verdict-keeping matches with a changed vote. R2 the hygiene assertions above.

READOUTS (the registration's C1-C4; C1 decides, C2-C4 are descriptive). C1: n2 = matches whose BOTH order votes changed, against the
EXACT CONDITIONAL NULL given the observed T (10^6 uniformly random T-subsets of the 600 cells, numpy default_rng(42), printed with its
Monte-Carlo error; the closed form P0(n2 = k) = C(M,k) C(M-k,T-2k) 2^(T-2k) / C(2M,T) printed beside as a check); the two-sided alpha-0.05
region is the upper tail n2 >= c with P0 <= 0.025 and the lower tail n2 <= c with P0 <= 0.025 WHERE ONE EXISTS; HELD iff n2 lies outside,
FAILED iff inside. n1 = T - 2 x n2 printed beside, deciding nothing. C2 the expected direct reversals among pass-1-decisive matches under
i.i.d. change at the measured transition matrix (pooled over the 600 cells; per-order beside), exp(-E) and the relayed 2.9 / exp(-2.9).
C3 the expected TIE <-> decisive share of verdict changes under the same model against the observed. C4 C1 on one match per question
(the first by match id). Support: the deciding denominator, Kish mean cluster size from the cache's own clusters, DEFF measured on the
cache pair (canary_baseline.clustered, a local AST-asserted copy, B 2000 seed 42, on the verdict-change indicator), n_eff, SD0 and
SD0 x sqrt(DEFF), and the MDE at 80% power (the Poisson alternative mean at which P(n2 >= c) = 0.80, minus E0; x sqrt(DEFF) beside).
"""
import os, sys, ast, math, json, random, hashlib, argparse, tempfile, shutil, io, contextlib, sqlite3
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import numpy as np
import pool_guard
import rejudge_grok as rj
import vote_frame_cert as vfc     # open_ro, stat_of, script_shas, connect_trap (no DB is opened at import)

TEST = "TIE-MECHANICS"
REGISTRATION = "docs/judge_v2_program.md L12911-L13030 (3c2fcab)"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
X12 = os.path.join("experiment_results", "x12_crossdomain")
CFG_OF_RECORD = dict(
    pool=pool_guard.MMLU_PRO_POOL,
    set_json=os.path.join(X12, "canary_set.json"), set_hash="50af669ac6997f9f",
    cache1=os.path.join(X12, "canary_baseline_pass1.db"), cache2=os.path.join(X12, "canary_baseline_pass2.db"),
    cache1_sha256="5142795bdc8c5a8ec8d09a3a4f9cd6c84de206834aeab7ca11cea4761000690c",
    out=os.path.join(X12, "tie_mechanics_outcome.txt"),
    n_matches=300, n_questions=279,
    recorded=dict(changes=26, tie_to_dec=16, dec_to_tie=10, dec_both=215, reversals=0, T=59, cells=600, keep_changed=23),
    draws=1_000_000, seed=42, boot_B=2000,
)
SCHEMA_EXEMPT = {"provider1", "provider2"}      # pass 1 predates them (canary_baseline.py docstring, [ADDED 2026-09-22])
READ_COLS = ("match_id", "model_a", "model_b", "qid", "winner", "flip", "invalid", "vote1", "vote2_raw", "finish1", "finish2", "stratum", "pair_kind")
DEC = ("Model A", "Model B")
LABELS = ("Model A", "Model B", "TIE", "INVALID")
ALPHA_TAIL = 0.025
# the registration's predictions and the relayed quantities (L12978-L12984, L12958-L12964)
P1_BAND = (8, 12); P2_BAND = (35, 43); P3_P = 0.001; P4_BAND = (0.02, 1.0); P4_P0 = 0.37; P5_SHARE = 0.90
RELAYED_UNCONDITIONAL = 2.9; PREDICTED_N2 = 10


# ── local copies asserted against canary_baseline.py's SOURCE (never imported) ──────────────────────────────────────────────────────

def set_hash(matches):
    canon = "\n".join("%d:%d:%s:%s:%s" % (m["match_id"], m["qid"], m["model_a"], m["model_b"], m["stratum"]) for m in matches)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def clustered(vals_by_q, stat, B=2000, seed=42):
    """Question-clustered bootstrap of stat(list of per-match values): resample questions with replacement."""
    qs = sorted(vals_by_q); rng = random.Random(seed); out = []
    for _ in range(B):
        bs = [v for _ in qs for v in vals_by_q[qs[rng.randrange(len(qs))]]]
        out.append(stat(bs))
    out.sort()
    mean = sum(out) / B; sd = (sum((x - mean) ** 2 for x in out) / (B - 1)) ** 0.5
    return out[int(0.025 * B)], out[int(0.975 * B) - 1], sd


def _fn_dump(src, name, drop_defaults=False):
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            if drop_defaults: node.args.defaults = []
            return ast.dump(node, annotate_fields=False)
    raise SystemExit("[SOURCE] %s not found" % name)


def assert_local_copies():
    """set_hash must be AST-identical to canary_baseline.set_hash; clustered identical up to its default seed (canary: seed=SEED=42)."""
    theirs = open(os.path.join(HERE, "canary_baseline.py"), encoding="utf-8").read()
    mine = open(os.path.abspath(__file__), encoding="utf-8").read()
    ok_hash = _fn_dump(theirs, "set_hash") == _fn_dump(mine, "set_hash")
    ok_clu = _fn_dump(theirs, "clustered", True) == _fn_dump(mine, "clustered", True)
    if not (ok_hash and ok_clu):
        raise SystemExit("[R2] REFUSED: the local copy of canary_baseline.%s drifted from its source" % ("set_hash" if not ok_hash else "clustered"))
    return "set_hash and clustered AST-identical to canary_baseline.py (clustered up to its default seed, canary SEED = 42)"


# ── loading and the gates ─────────────────────────────────────────────────────────────────────────────────────────────────────────

def load_cache(path):
    con = vfc.open_ro(path)
    try:
        cols = [(r[1], r[2]) for r in con.execute("PRAGMA table_info(verdicts)")]
        rows = [dict(zip(READ_COLS, r)) for r in con.execute("SELECT %s FROM verdicts" % ", ".join(READ_COLS))]
    finally:
        con.close()
    return cols, rows


def name_of(r, w):
    return {"Model A": r["model_a"], "Model B": r["model_b"]}.get(w, w)


def canary_winner(r):
    v1 = "INVALID" if r["finish1"] == "length" else r["vote1"]
    v2 = "INVALID" if r["finish2"] == "length" else r["vote2_raw"]
    return name_of(r, rj.combine_orders(v1, v2)[0])


def counts(p1, p2):
    """The canary's aggregation (convention B: pairs valid in both passes), cell-level changes and the C1 statistic."""
    paired = [(p1[k], p2[k]) for k in sorted(p1) if k in p2 and not p1[k]["invalid"] and not p2[k]["invalid"]]
    dec = lambda w: w not in ("TIE", "INVALID")
    ch = [(a, b) for a, b in paired if a["winner"] != b["winner"]]
    c = dict(paired=len(paired), changes=len(ch),
             tie_to_dec=sum(1 for a, b in ch if a["winner"] == "TIE" and dec(b["winner"])),
             dec_to_tie=sum(1 for a, b in ch if dec(a["winner"]) and b["winner"] == "TIE"),
             dec_both=sum(1 for a, b in paired if dec(a["winner"]) and dec(b["winner"])),
             reversals=sum(1 for a, b in paired if dec(a["winner"]) and dec(b["winner"]) and a["winner"] != b["winner"]),
             cells=2 * len(paired))
    c1 = [int(a["vote1"] != b["vote1"]) for a, b in paired]; c2 = [int(a["vote2_raw"] != b["vote2_raw"]) for a, b in paired]
    c["T"] = sum(c1) + sum(c2)
    c["n2"] = sum(1 for x, y in zip(c1, c2) if x and y)
    c["n_any"] = sum(1 for x, y in zip(c1, c2) if x or y)
    c["n1"] = c["n_any"] - c["n2"]
    c["keep_changed"] = sum(1 for (a, b), x, y in zip(paired, c1, c2) if a["winner"] == b["winner"] and (x or y))
    return c, paired


def schema_check(s1, s2):
    """Ruling (1) (04379d7): every column's NAME, declared TYPE and ORDER identical in the two caches, except exactly SCHEMA_EXEMPT, which
    may be absent from PASS 1 ONLY. s1, s2: ordered lists of (name, type) from PRAGMA table_info. -> (ok, printed reason)."""
    e1 = [c for c in s1 if c[0] in SCHEMA_EXEMPT]; e2 = [c for c in s2 if c[0] in SCHEMA_EXEMPT]
    if e1:
        if s1 == s2: return True, "identical in name, type and order (the exempt columns present in both)"
        return False, "pass 1 carries %s, so it must equal pass 2 in full, and does not" % e1
    f1 = list(s1); f2 = [c for c in s2 if c[0] not in SCHEMA_EXEMPT]
    if f1 != f2:
        i = next((k for k in range(min(len(f1), len(f2))) if f1[k] != f2[k]), min(len(f1), len(f2)))
        return False, ("outside %s the ordered (name, type) lists differ at position %d: pass 1 %s | pass 2 %s"
                       % (sorted(SCHEMA_EXEMPT), i, f1[i] if i < len(f1) else "(end)", f2[i] if i < len(f2) else "(end)"))
    return True, ("identical in name, type and order except the columns EXCLUDED from the comparison, absent from pass 1 only: %s"
                  % ([c for c in e2] or "none"))


def gates(cfg, root, say, pool_check=True, guard=None):
    """R2 then R1. -> (p1, p2, counts, paired, schema lines); raises SystemExit on any failed gate (nothing is written)."""
    if pool_check:
        (guard or pool_guard.assert_pool_of_record)(cfg["pool"])
    say("[POOL] %s (pool of record; pool_guard.assert_pool_of_record passed)" % cfg["pool"])
    say("[COPIES] " + assert_local_copies())
    sj = json.load(open(os.path.join(root, cfg["set_json"]), encoding="utf-8"))
    h = set_hash(sj["matches"])
    if sj.get("pool_id") != cfg["pool"] or h != cfg["set_hash"] or sj.get("set_hash") != cfg["set_hash"]:
        raise SystemExit("[R2] REFUSED: %s hashes to %s (file says %s, pool %s); the set of record is %s on %s"
                         % (cfg["set_json"], h, sj.get("set_hash"), sj.get("pool_id"), cfg["set_hash"], cfg["pool"]))
    say("[SET] %s re-hashed with set_hash(): %s = the hash of record; %d matches" % (cfg["set_json"].replace("\\", "/"), h, len(sj["matches"])))
    want = {(m["match_id"], m["qid"], m["model_a"], m["model_b"], m["stratum"]) for m in sj["matches"]}
    paths = [os.path.join(root, cfg["cache1"]), os.path.join(root, cfg["cache2"])]
    st0 = {p: vfc.stat_of(p) for p in paths}
    for p in paths: say("[CACHE] %s before: %s" % (vfc.rel(p, root), st0[p]))
    sha1 = hashlib.sha256(open(paths[0], "rb").read()).hexdigest()
    if cfg.get("cache1_sha256") and sha1 != cfg["cache1_sha256"]:
        raise SystemExit("[R2] REFUSED: pass 1 sha256 %s is not the READY's %s" % (sha1, cfg["cache1_sha256"]))
    say("[CACHE] pass 1 sha256 %s (= the pass-2 READY's); pass 2 sha256 %s" % (sha1, hashlib.sha256(open(paths[1], "rb").read()).hexdigest()))
    (s1, r1), (s2, r2) = load_cache(paths[0]), load_cache(paths[1])
    ok, why = schema_check(s1, s2)
    say("[SCHEMA] table verdicts (the table the counts read; run_meta is not compared): pass 1 %d columns, pass 2 %d columns: %s" % (len(s1), len(s2), why))
    if not ok:
        raise SystemExit("[R1] REFUSED: the two schemas differ: %s" % why)
    for tag, rows in (("pass 1", r1), ("pass 2", r2)):
        ids = [r["match_id"] for r in rows]
        if len(rows) != cfg["n_matches"] or len(set(ids)) != cfg["n_matches"]:
            raise SystemExit("[R2] REFUSED: %s holds %d rows / %d distinct match ids, not %d" % (tag, len(rows), len(set(ids)), cfg["n_matches"]))
        got = {(r["match_id"], r["qid"], r["model_a"], r["model_b"], r["stratum"]) for r in rows}
        if got != want:
            raise SystemExit("[R2] REFUSED: %s rows are not the set of record (%d differ)" % (tag, len(got ^ want)))
        bad = [r["match_id"] for r in rows if canary_winner(r) != r["winner"]]
        if bad:
            raise SystemExit("[R2] REFUSED: %s: %d stored winners are not the canary's aggregation of (vote1, vote2_raw) (first %s): the frame "
                             "is not the one the canary's script used" % (tag, len(bad), bad[:10]))
        say("[FRAME] %s: %d rows, %d distinct match ids; every stored winner = name_of(combine_orders(vote1, vote2_raw)) (%d rows)"
            % (tag, len(rows), len(set(ids)), len(rows)))
    p1 = {r["match_id"]: r for r in r1}; p2 = {r["match_id"]: r for r in r2}
    c, paired = counts(p1, p2)
    rec = cfg["recorded"]
    miss = {k: (c[k], v) for k, v in rec.items() if c[k] != v}
    say("[R1] recomputed: %d verdict changes (%d TIE->decisive, %d decisive->TIE) | %d decisive in both | %d direct reversals | %d of %d order votes "
        "changed | %d verdict-keeping matches with a changed vote | recorded %s"
        % (c["changes"], c["tie_to_dec"], c["dec_to_tie"], c["dec_both"], c["reversals"], c["T"], c["cells"], c["keep_changed"], rec))
    if miss:
        raise SystemExit("[R1] REFUSED: the recorded counts are not reproduced (computed, recorded): %s; no outcome is written" % miss)
    say("[R1] HELD: every recorded count reproduced exactly")
    st1 = {p: vfc.stat_of(p) for p in paths}
    for p in paths:
        say("[CACHE] %s after: %s -> %s" % (vfc.rel(p, root), st1[p], "unchanged" if st1[p] == st0[p] else "CHANGED"))
        if st1[p] != st0[p]: raise SystemExit("[R2] REFUSED: %s changed under the read" % vfc.rel(p, root))
    return p1, p2, c, paired, (s1, s2)


# ── the null ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def null_exact(M, T):
    tot = math.comb(2 * M, T)
    return [math.comb(M, k) * math.comb(M - k, T - 2 * k) * 2 ** (T - 2 * k) / tot for k in range(0, T // 2 + 1)] if T <= 2 * M else []


def null_mc(M, T, draws, seed, chunk=50_000):
    """Uniformly random T-subsets of the 2M (match, order) cells; cell 2m and 2m+1 are match m's two orders. -> pmf array."""
    rng = np.random.default_rng(seed)
    cnt = np.zeros(T // 2 + 2, dtype=np.int64); done = 0
    while done < draws:
        b = min(chunk, draws - done)
        U = rng.random((b, 2 * M), dtype=np.float32)
        idx = np.argpartition(U, T - 1, axis=1)[:, :T] // 2 if T > 0 else np.zeros((b, 0), dtype=np.int64)
        s = np.sort(idx, axis=1)
        n2 = (s[:, 1:] == s[:, :-1]).sum(axis=1) if T > 1 else np.zeros(b, dtype=np.int64)
        cnt += np.bincount(n2, minlength=len(cnt))[:len(cnt)]
        done += b
    return cnt / draws


def region(pmf):
    """Two-sided alpha-0.05 rejection region: (upper c or None, lower c or None) with tail P0 <= 0.025 each."""
    up = None
    for c in range(len(pmf)):
        if sum(pmf[c:]) <= ALPHA_TAIL: up = c; break
    lo = None
    for c in range(len(pmf) - 1, -1, -1):
        if sum(pmf[:c + 1]) <= ALPHA_TAIL: lo = c; break
    return up, lo


def c1_verdict(n2, up, lo):
    inside = (up is not None and n2 >= up) or (lo is not None and n2 <= lo)
    return "FAILED" if inside else "HELD"


def c1_lines(tag, M, T, n2, draws, seed, pmf_mc=None):
    pmf = pmf_mc if pmf_mc is not None else null_mc(M, T, draws, seed)
    ex = null_exact(M, T)
    up, lo = region(pmf); upx, lox = region(ex)
    e0 = M * T * (T - 1) / (2 * M * (2 * M - 1))
    mean_mc = float(sum(k * p for k, p in enumerate(pmf))); sd_mc = float(sum((k - mean_mc) ** 2 * p for k, p in enumerate(pmf))) ** 0.5
    p_up = float(sum(pmf[n2:])) if n2 < len(pmf) else 0.0
    p_up_x = sum(ex[n2:]) if n2 < len(ex) else 0.0
    mcse = (p_up * (1 - p_up) / draws) ** 0.5
    v = c1_verdict(n2, up, lo)
    L = ["%s n2 = %d matches with BOTH order votes changed, of M = %d matches, given T = %d changed cells of %d; n1 = T - 2 x n2 = %d (decides nothing)"
         % (tag, n2, M, T, 2 * M, T - 2 * n2),
         "%s EXACT CONDITIONAL NULL by Monte Carlo: %d uniformly random %d-subsets of the %d cells (numpy default_rng(%d)): E0 %.3f (closed form "
         "M T (T-1) / (N (N-1)) = %.3f), SD0 %.3f; P0(n2 >= %d) = %.5f (MC SE %.5f; closed form %.5f)" % (tag, draws, T, 2 * M, seed, mean_mc, e0, sd_mc, n2, p_up, mcse, p_up_x),
         "%s null pmf P0(n2 = 0..%d): MC %s | closed form %s" % (tag, min(12, len(pmf) - 1), " ".join("%.4f" % x for x in pmf[:13]), " ".join("%.4f" % x for x in ex[:13])),
         "%s two-sided alpha-0.05 region (each tail <= 0.025): upper n2 >= %s (P0 %.4f)%s; lower %s%s" % (tag, up, float(sum(pmf[up:])) if up is not None else float("nan"),
             "" if up == upx else " [closed form %s]" % upx,
             ("n2 <= %d (P0 %.4f)" % (lo, float(sum(pmf[:lo + 1])))) if lo is not None else "NONE",
             "" if lo == lox else " [closed form %s]" % lox)]
    if lo is None:
        L.append("%s NO LOWER REJECTION REGION: P0(n2 = 0) = %.4f > 0.025, so a DEFICIT of double changes (the orders changing together LESS "
                 "than independence allows) CANNOT BE SEEN at T = %d, whatever the data" % (tag, float(pmf[0]), T))
    else:
        L.append("%s a lower region exists at this T (n2 <= %d): a deficit of double changes is detectable here" % (tag, lo))
    return v, L, dict(e0=e0, sd0=sd_mc, up=up, lo=lo, p=p_up, p_exact=p_up_x, pmf=pmf, ex=ex)


# ── C2 / C3: the i.i.d. model at the measured transition matrix ─────────────────────────────────────────────────────────────────────

def transition(paired):
    per = {1: Counter(), 2: Counter()}
    for a, b in paired:
        per[1][(a["vote1"], b["vote1"])] += 1; per[2][(a["vote2_raw"], b["vote2_raw"])] += 1
    pooled = per[1] + per[2]
    def probs(C):
        tot = Counter()
        for (x, _), n in C.items(): tot[x] += n
        return {(x, y): C[(x, y)] / tot[x] for x in LABELS for y in LABELS if tot[x]}
    return per, pooled, probs(pooled), {k: probs(v) for k, v in per.items()}


def expected_reversals(paired, P1, P2):
    e = 0.0; n = 0
    for a, _ in paired:
        w = rj.combine_orders(a["vote1"], a["vote2_raw"])[0]
        if w not in DEC: continue
        n += 1
        v1, v2 = a["vote1"], a["vote2_raw"]
        e += P1.get((v1, vj(v1)), 0.0) * P2.get((v2, vj(v2)), 0.0)
    return e, n


def vj(v):
    return {"Model A": "Model B", "Model B": "Model A"}.get(v, v)


def expected_composition(paired, P1, P2):
    """-> (E[changes], E[TIE<->decisive], E[decisive<->decisive], E[involving INVALID])."""
    ch = td = dd = iv = 0.0
    for a, _ in paired:
        w = rj.combine_orders(a["vote1"], a["vote2_raw"])[0]
        for y1 in LABELS:
            q1 = P1.get((a["vote1"], y1), 0.0)
            if not q1: continue
            for y2 in LABELS:
                q = q1 * P2.get((a["vote2_raw"], y2), 0.0)
                if not q: continue
                w2 = rj.combine_orders(y1, y2)[0]
                if w2 == w: continue
                ch += q
                if "INVALID" in (w, w2): iv += q
                elif (w == "TIE") != (w2 == "TIE"): td += q
                else: dd += q
    return ch, td, dd, iv


# ── support ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def poisson_sf(c, mu):
    return 1.0 - sum(math.exp(-mu) * mu ** k / math.factorial(k) for k in range(c))


def mu_for_power(c, power=0.80):
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if poisson_sf(c, mid) < power: lo = mid
        else: hi = mid
    return (lo + hi) / 2


def support_lines(paired, nulls, cfg, boot_B):
    byq = defaultdict(list)
    for a, b in paired: byq[a["qid"]].append(int(a["winner"] != b["winner"]))
    n = len(paired); nq = len(byq)
    sizes = Counter(len(v) for v in byq.values())
    kish = sum(len(v) ** 2 for v in byq.values()) / n
    f = sum(sum(v) for v in byq.values()) / n
    lo_, hi_, sd = clustered(byq, lambda xs: sum(xs) / len(xs), B=boot_B, seed=cfg["seed"])
    bino = (f * (1 - f) / n) ** 0.5
    deff = (sd / bino) ** 2 if bino > 0 else float("nan")
    neff = n / deff if deff == deff and deff > 0 else float("nan")
    e0, sd0, up = nulls["e0"], nulls["sd0"], nulls["up"]
    mu80 = mu_for_power(up) if up is not None else float("nan")
    mde = mu80 - e0; mde_d = mde * deff ** 0.5 if deff == deff else float("nan")
    dist = PREDICTED_N2 - e0
    scoreable = dist > mde_d
    L = ["SUPPORT (measured on this cache pair; beside the deciding statistic):",
         "  (a) deciding denominator: %d matches = %d (match, order) cells on %d questions; cluster sizes %s; sum n^2 = %d; KISH MEAN CLUSTER SIZE %.3f"
         % (n, 2 * n, nq, "/".join("%d:%d" % (s, sizes[s]) for s in sorted(sizes)), sum(len(v) ** 2 for v in byq.values()), kish),
         "  (b) DEFF %.2f MEASURED on this pair: the question-clustered bootstrap of the verdict-change indicator (canary_baseline.clustered, B %d, seed %d): "
         "floor %.3f [%.3f, %.3f] SE %.4f against the binomial SE %.4f (registered: DEFF 1.09 from CANARY-BASELINE pass 2)" % (deff, boot_B, cfg["seed"], f, lo_, hi_, sd, bino),
         "  (c) n_eff = %d / %.2f = %.0f" % (n, deff, neff),
         "  (d) SD0(n2 | T) = %.3f (the exact conditional null above); carried at the measured DEFF: %.3f x sqrt(%.2f) = %.3f" % (sd0, sd0, deff, sd0 * deff ** 0.5),
         "  (e) MDE at 80%% power: the Poisson alternative mean at which P(n2 >= %s) = 0.80 is %.2f, an excess of %.2f - %.3f = %.2f double-change matches; "
         "%.2f with the DEFF carried (x sqrt(%.2f)). A DEFICIT has no MDE at this n: it is not detectable at all." % (up, mu80, mu80, e0, mde, mde_d, deff),
         "  (f) verdict line at the measured support: C1 prediction %d against E0 %.3f, distance %.2f %s MDE %.2f -> %s (margin %.2f); C2, C3, C4 DESCRIPTIVE-ONLY"
         % (PREDICTED_N2, e0, dist, ">" if scoreable else "<=", mde_d, "SCOREABLE" if scoreable else "NOT SCOREABLE at the measured support (C1 is still read by its registered rule)", dist - mde_d),
         "  (g) structural: n is fixed at %d by the frozen set; at this T only an EXCESS of double changes is detectable; the deficit reading is reachable "
         "only with further retest passes (not bought)" % n]
    return L, dict(deff=deff, neff=neff, kish=kish, mde=mde, mde_d=mde_d, scoreable=scoreable)


# ── scoring (every branch printed; the selftest executes both sides of each) ─────────────────────────────────────────────────────

def score_predictions(n2, n1, c1v, p_exact, e_rev, share):
    hf = lambda b: "HELD" if b else "FAILED"
    return [("P1", hf(P1_BAND[0] <= n2 <= P1_BAND[1]), "P1 %s: n2 = %d (registered 10, interval [%d, %d])" % (hf(P1_BAND[0] <= n2 <= P1_BAND[1]), n2, *P1_BAND)),
            ("P2", hf(P2_BAND[0] <= n1 <= P2_BAND[1]), "P2 %s: n1 = %d (registered 39, interval [%d, %d])" % (hf(P2_BAND[0] <= n1 <= P2_BAND[1]), n1, *P2_BAND)),
            ("P3", hf(c1v == "FAILED" and p_exact <= P3_P), "P3 %s: C1 %s with exact conditional p %.2g (registered: C1 FAILED, p <= %g)"
             % (hf(c1v == "FAILED" and p_exact <= P3_P), c1v, p_exact, P3_P)),
            ("P4", hf(P4_BAND[0] <= e_rev <= P4_BAND[1] and math.exp(-e_rev) >= P4_P0), "P4 %s: E_rev %.4f, P(0 | E_rev) = %.3f (registered E_rev in [%.2f, %.1f], "
             "point 0.25, P(0) >= %.2f)" % (hf(P4_BAND[0] <= e_rev <= P4_BAND[1] and math.exp(-e_rev) >= P4_P0), e_rev, math.exp(-e_rev), P4_BAND[0], P4_BAND[1], P4_P0)),
            ("P5", hf(share >= P5_SHARE), "P5 %s: expected TIE <-> decisive share of verdict changes under i.i.d. = %.4f (registered >= %.2f)" % (hf(share >= P5_SHARE), share, P5_SHARE))]


def consequence_lines(c1v):
    if c1v == "HELD":
        return ["FALSIFIER: NOT FIRED. C1 HELD licenses, ON THIS SET, deriving a match-level floor from the per-call rate by independence arithmetic; "
                "EITHER WAY NO RECORDED NUMBER MOVES (canary floor 0.087 [0.056, 0.122], NO ALARM, 26 / 215 / 0, 0.098, DECOMP 5.7%, "
                "BFCL-FLIP-RESEED's anchor 0.913).",
                "CONSEQUENCE FOR TRACE-TRUNCATION: C1 HELD -> the per-call change rate is a TRANSFERABLE parameter under independence; its retest floor "
                "may be restated as a function of p (a match-level verdict change of about 2p(1 - p) under the tie rule) and the item re-priced or "
                "dropped AT ZERO COST by the cost-estimator and the experiment-manager, with an insertion into its queue note."]
    return ["FALSIFIER: FIRED. C1 FAILED overturns the reading (a relayed lead, never a recorded result) that the canary's tie-boundary pattern is "
            "forced arithmetic of independent per-call flips, and forbids deriving any match-level floor from a per-call rate (0.098, or DECOMP's "
            "per-call 0.057) by independence arithmetic anywhere in the record; EITHER WAY NO RECORDED NUMBER MOVES (canary floor 0.087 [0.056, "
            "0.122], NO ALARM, 26 / 215 / 0, 0.098, DECOMP 5.7%, BFCL-FLIP-RESEED's anchor 0.913).",
            "CONSEQUENCE FOR TRACE-TRUNCATION: C1 FAILED -> the per-call rate does NOT transfer; no match-level floor may be derived from 0.098 or "
            "0.057 by independence arithmetic; TRACE-TRUNCATION's floor stays a per-match retest quantity (CANARY 0.087, DECOMP 5.7%) and its "
            "\"re-price after TIE-MECHANICS\" resolves to NO RE-PRICE FROM THIS TEST."]


# ── the modes ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

def dry_run(cfg=None, root=None, pool_check=True):
    cfg = cfg or CFG_OF_RECORD; root = root or DATA_ROOT
    say = lambda s: print(s, flush=True)
    lf, crlf = vfc.script_shas(__file__)
    p1, p2, c, paired, (s1, s2) = gates(cfg, root, say, pool_check)
    say("[DRY-RUN] %s | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) | pass 1 schema %s | pass 2 schema %s" % (TEST, lf, crlf, [x for x, _ in s1], [x for x, _ in s2]))
    say("[DRY-RUN] zero calls; nothing written; the R1 counts above are the gate the run will apply")
    return 0


def analyze(cfg=None, root=None, pool_check=True, out_path=None, guard=None):
    cfg = cfg or CFG_OF_RECORD; root = root or DATA_ROOT
    out = out_path or os.path.join(root, cfg["out"])
    if os.path.exists(out):
        raise SystemExit("[WRITE-ONCE] REFUSED: %s exists; the outcome of record is never rewritten" % vfc.rel(out, root))
    L = []
    def say(s):
        L.append(s); print(s, flush=True)
    lf, crlf = vfc.script_shas(__file__)
    p1, p2, c, paired, _ = gates(cfg, root, say, pool_check, guard)
    say("=== %s (zero calls) | registration %s | script sha256[:16] of the LF bytes %s (of the CRLF rendering %s) ===" % (TEST, REGISTRATION, lf, crlf))
    M = len(paired)
    say("")
    say("(C1) THE DECIDING STATISTIC")
    c1v, c1L, nul = c1_lines("  C1", M, c["T"], c["n2"], cfg["draws"], cfg["seed"])
    for l in c1L: say(l)
    sL, sup = support_lines(paired, nul, cfg, cfg["boot_B"])
    for l in sL: say("  " + l)
    say("  C1 %s: n2 = %d is %s the rejection region (exact conditional p = %.2g by MC, %.2g closed form; DEFF %.2f, n_eff %.0f, MDE %.2f beside)"
        % (c1v, c["n2"], "INSIDE" if c1v == "FAILED" else "OUTSIDE", nul["p"], nul["p_exact"], sup["deff"], sup["neff"], sup["mde_d"]))
    say("  reading: %s" % ("within-match dependence: the two orders of a match change TOGETHER more often than independent per-call change allows (a "
                           "property of the judge on these matches)" if c1v == "FAILED" else
                           "the i.i.d. per-call model is consistent: the canary pattern is arithmetic the tie rule forces"))
    say("")
    per, pooled, P, Pk = transition(paired)
    say("(C2) THE REVERSAL CELL, DESCRIPTIVE-ONLY")
    say("  measured transition counts (pass 1 -> pass 2) pooled over the %d cells: %s" % (c["cells"], {"%s->%s" % k: v for k, v in sorted(pooled.items()) if k[0] != k[1]}))
    for o in (1, 2): say("  order %d: %s" % (o, {"%s->%s" % k: v for k, v in sorted(per[o].items()) if k[0] != k[1]}))
    e_rev, n_dec1 = expected_reversals(paired, P, P)
    e_rev_k, _ = expected_reversals(paired, Pk[1], Pk[2])
    say("  E_rev = %.4f expected direct reversals among the %d pass-1-decisive matches (pooled matrix; per-order matrices %.4f); observed %d; "
        "P(0 | E_rev) = exp(-E_rev) = %.3f" % (e_rev, n_dec1, e_rev_k, c["reversals"], math.exp(-e_rev)))
    say("  the relayed unconditional %.1f (every double change; an upper bound on the reversal expectation): exp(-%.1f) = %.3f > 0.05, so no "
        "expectation at or below %.1f can make \"0 reversals\" significant" % (RELAYED_UNCONDITIONAL, RELAYED_UNCONDITIONAL, math.exp(-RELAYED_UNCONDITIONAL), RELAYED_UNCONDITIONAL))
    say("")
    say("(C3) THE VERDICT-CHANGE COMPOSITION, DESCRIPTIVE")
    ech, etd, edd, eiv = expected_composition(paired, P, P)
    share = etd / ech if ech else float("nan")
    say("  under i.i.d. at the pooled matrix: E[verdict changes] %.2f = TIE<->decisive %.2f + decisive<->decisive %.3f + involving INVALID %.3f; "
        "expected TIE<->decisive share %.4f | observed %d of %d" % (ech, etd, edd, eiv, share, c["tie_to_dec"] + c["dec_to_tie"], c["changes"]))
    say("")
    say("(C4) SENSITIVITY, DESCRIPTIVE: one match per question (the first by match id)")
    firsts = {}
    for a, b in paired:
        if a["qid"] not in firsts or a["match_id"] < firsts[a["qid"]][0]["match_id"]: firsts[a["qid"]] = (a, b)
    sub = sorted(firsts.values(), key=lambda ab: ab[0]["match_id"])
    T4 = sum(int(a["vote1"] != b["vote1"]) + int(a["vote2_raw"] != b["vote2_raw"]) for a, b in sub)
    n24 = sum(1 for a, b in sub if a["vote1"] != b["vote1"] and a["vote2_raw"] != b["vote2_raw"])
    c4v, c4L, _ = c1_lines("  C4", len(sub), T4, n24, cfg["draws"], cfg["seed"])
    for l in c4L: say(l)
    say("  C4 reading (descriptive): n2 = %d would be %s the region of its own conditional null" % (n24, "INSIDE" if c4v == "FAILED" else "OUTSIDE"))
    say("")
    say("PREDICTIONS")
    for _, _, l in score_predictions(c["n2"], c["n1"], c1v, nul["p_exact"], e_rev, share): say("  " + l)
    say("")
    say("CRITERION C1: %s" % c1v)
    for l in consequence_lines(c1v): say(l)
    say("WHAT THIS RUN WILL NOT SHOW: why the orders co-vary (dependence, not mechanism); anything about another corpus, judge or set; that 0 "
        "reversals is a judge property (a deficit of double changes is structurally undetectable here); any fidelity or accuracy number.")
    with open(out, "x", encoding="utf-8") as f: f.write("\n".join(L) + "\n")
    print("[WRITTEN] %s (write-once)" % vfc.rel(out, root), flush=True)
    return dict(c1=c1v, n2=c["n2"], T=c["T"], c4=c4v, e_rev=e_rev, share=share, support=sup, text="\n".join(L))


# ── selftest ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────

CANARY_DDL = ("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, node_id TEXT, qid INTEGER, anchor TEXT, "
              "ref_letter TEXT, ref_correct INTEGER, vote1 TEXT, vote2_raw TEXT, conf1 REAL, conf2 REAL, winner TEXT, flip INTEGER, invalid INTEGER, "
              "raw1 TEXT, raw2 TEXT, ts REAL, finish1 TEXT, finish2 TEXT, ctok1 INTEGER, ctok2 INTEGER, stratum TEXT, pair_kind TEXT%s);"
              "CREATE TABLE run_meta (key TEXT PRIMARY KEY, value TEXT);")


def _fixture(root, dependent, seed):
    """A synthetic canary pair: 300 matches on 279 questions; pass 2 changes cells independently (p 0.1) or, when dependent, changes BOTH
    orders of 12 matches plus single cells elsewhere. -> (cfg, truth)."""
    g = random.Random(seed)
    x12 = os.path.join(root, X12); os.makedirs(x12, exist_ok=True)
    matches = []
    for i in range(300):
        q = 1000 + (i if i < 279 else i - 279)
        matches.append(dict(match_id=5000 + i, qid=q, model_a="ma%d" % (i % 7), model_b="mb%d" % (i % 5), node_id="n", anchor="Law",
                            stratum="cross" if i % 2 else "contested", pair_kind="cross"))
    json.dump(dict(pool_id="p_selftest", set_hash=set_hash(matches), matches=matches), open(os.path.join(x12, "canary_set.json"), "w"))
    def votes():
        return g.choice([("Model A", "Model B"), ("Model B", "Model A"), ("Model A", "Model A"), ("Model B", "Model B"), ("TIE", "Model A")])
    other = lambda v: g.choice([x for x in ("Model A", "Model B", "TIE") if x != v])
    p1v = [votes() for _ in matches]
    p2v = []
    both = set(g.sample(range(300), 12)) if dependent else set()
    for i, (a, b) in enumerate(p1v):
        if dependent:
            if i in both: p2v.append((other(a), other(b)))
            elif g.random() < 0.08: p2v.append((other(a), b) if g.random() < 0.5 else (a, other(b)))
            else: p2v.append((a, b))
        else:
            p2v.append((other(a) if g.random() < 0.1 else a, other(b) if g.random() < 0.1 else b))
    for n, vv, extra in ((1, p1v, ""), (2, p2v, ", provider1 TEXT, provider2 TEXT")):
        con = sqlite3.connect(os.path.join(x12, "canary_baseline_pass%d.db" % n)); con.executescript(CANARY_DDL % extra)
        for m, (v1, v2) in zip(matches, vv):
            w, f, inv = rj.combine_orders(v1, v2)
            row = [m["match_id"], m["model_a"], m["model_b"], "n", m["qid"], "Law", "A", 1, v1, v2, 0.8, 0.8,
                   {"Model A": m["model_a"], "Model B": m["model_b"]}.get(w, w), int(f), int(inv), "r1", "r2", 0.0, "stop", "stop", 1, 1,
                   m["stratum"], "cross"] + (["azure:x", "azure:x"] if n == 2 else [])
            con.execute("INSERT INTO verdicts VALUES (%s)" % ",".join("?" * len(row)), row)
        con.commit(); con.close()
    cfg = dict(CFG_OF_RECORD, pool="p_selftest", set_hash=set_hash(matches), cache1_sha256=None, draws=100_000, boot_B=400,
               out=os.path.join(X12, "tie_mechanics_outcome.txt"))
    # the fixture's own counts are its "record" (so R1's pass branch executes); a mismatched record executes its refusal branch
    p1 = {m["match_id"]: dict(zip(READ_COLS, [m["match_id"], m["model_a"], m["model_b"], m["qid"],
            {"Model A": m["model_a"], "Model B": m["model_b"]}.get(rj.combine_orders(*v)[0], rj.combine_orders(*v)[0]), 0, 0, v[0], v[1], "stop", "stop", m["stratum"], "cross"]))
          for m, v in zip(matches, p1v)}
    p2 = {m["match_id"]: dict(zip(READ_COLS, [m["match_id"], m["model_a"], m["model_b"], m["qid"],
            {"Model A": m["model_a"], "Model B": m["model_b"]}.get(rj.combine_orders(*v)[0], rj.combine_orders(*v)[0]), 0, 0, v[0], v[1], "stop", "stop", m["stratum"], "cross"]))
          for m, v in zip(matches, p2v)}
    cc, _ = counts(p1, p2)
    cfg["recorded"] = {k: cc[k] for k in CFG_OF_RECORD["recorded"]}
    return cfg, cc


def selftest():
    tmp = tempfile.mkdtemp(prefix="tiemech_selftest_")
    ok = True; lines = []
    def check(cond, what):
        nonlocal ok
        lines.append("  [%s] %s" % ("PASS" if cond else "FAIL", what)); ok = ok and bool(cond)
    try:
        with vfc.connect_trap(tmp):
            check(bool(assert_local_copies()), "local set_hash / clustered are AST-identical to canary_baseline.py's")
            # (1) i.i.d. pair must read HELD; (2) co-varying pair must read FAILED
            res = {}
            for tag, dep, seed in (("iid", False, 3), ("dependent", True, 5)):
                r = os.path.join(tmp, tag); os.makedirs(r)
                cfg, cc = _fixture(r, dep, seed)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    res[tag] = analyze(cfg, r, pool_check=False)
                txt = open(os.path.join(r, cfg["out"]), encoding="utf-8").read()
                res[tag]["txt"] = txt; res[tag]["cc"] = cc
            check(res["iid"]["c1"] == "HELD", "i.i.d. pair: C1 HELD (n2 %d at T %d)" % (res["iid"]["n2"], res["iid"]["T"]))
            check(res["dependent"]["c1"] == "FAILED", "co-varying pair: C1 FAILED (n2 %d at T %d)" % (res["dependent"]["n2"], res["dependent"]["T"]))
            for tag, want in (("iid", "NOT FIRED"), ("dependent", "FIRED.")):
                t = res[tag]["txt"]
                check(("FALSIFIER: %s" % want) in t and "CONSEQUENCE FOR TRACE-TRUNCATION: C1 %s" % res[tag]["c1"] in t,
                      "%s: falsifier and TRACE-TRUNCATION consequence lines printed for C1 %s" % (tag, res[tag]["c1"]))
                check(all(s in t for s in ("(C2)", "(C3)", "(C4)", "SUPPORT", "KISH MEAN CLUSTER SIZE", "DEFF", "n_eff", "MDE at 80%", "PREDICTIONS",
                                           "P1 ", "P2 ", "P3 ", "P4 ", "P5 ")),
                      "%s: C2-C4, the support readout (Kish, DEFF, n_eff, MDE) and P1-P5 printed" % tag)
            lower = [(tag, "C1 a lower region exists" in res[tag]["txt"], "C1 NO LOWER REJECTION REGION" in res[tag]["txt"]) for tag in ("iid", "dependent")]
            check(any(a for _, a, _ in lower) and any(b for _, _, b in lower) and all(a != b for _, a, b in lower),
                  "both lower-region branches of C1 executed on real fixtures (T 64: a lower region exists; T 50: NO LOWER REJECTION REGION): %s" % lower)
            check(("SCOREABLE" in res["iid"]["txt"]), "the measured verdict line is printed")
            # R1 refusal: a record that the caches do not reproduce writes nothing
            r = os.path.join(tmp, "r1"); os.makedirs(r); cfg, cc = _fixture(r, False, 3)
            cfg["recorded"] = dict(cfg["recorded"], changes=cfg["recorded"]["changes"] + 1)
            refused = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(cfg, r, pool_check=False)
            except SystemExit as e:
                refused = "[R1] REFUSED" in str(e)
            check(refused and not os.path.exists(os.path.join(r, cfg["out"])), "R1 refusal: an unreproduced record count writes no outcome")
            # T-C2: the pool guard and the pass-1 sha256 gate, both branches, by execution (an injected guard; no DB of record)
            r = os.path.join(tmp, "pg"); os.makedirs(r); cfg, cc = _fixture(r, False, 3)
            called = []
            cfg_sha = dict(cfg, cache1_sha256=hashlib.sha256(open(os.path.join(r, cfg["cache1"]), "rb").read()).hexdigest())
            with contextlib.redirect_stdout(io.StringIO()):
                gates(cfg_sha, r, lambda s: None, pool_check=True, guard=called.append)
            check(called == ["p_selftest"], "pool guard INVOKED on the pool of the set (%s); the pass-1 sha256 equal to the pinned one ADMITS" % called)
            def refuse_pool(x): raise SystemExit("[POOL-GUARD] stub refusal for %s" % x)
            pg_ref = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): gates(cfg_sha, r, lambda s: None, pool_check=True, guard=refuse_pool)
            except SystemExit as e: pg_ref = "stub refusal" in str(e)
            check(pg_ref, "a pool-guard refusal STOPS the gates before any cache is read")
            sha_ref = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): gates(dict(cfg, cache1_sha256="0" * 64), r, lambda s: None, pool_check=True, guard=called.append)
            except SystemExit as e: sha_ref = "pass 1 sha256" in str(e)
            check(sha_ref, "the pass-1 sha256 REFUSAL branch: a pass-1 cache whose sha256 is not the READY's is refused (R2)")
            # R2 refusals: a wrong set hash; a schema difference outside the exemption; a stored winner off the aggregation
            r = os.path.join(tmp, "r2"); os.makedirs(r); cfg, cc = _fixture(r, False, 3)
            bad = dict(cfg, set_hash="0000000000000000"); refused = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(bad, r, pool_check=False)
            except SystemExit as e: refused = "[R2]" in str(e)
            check(refused, "R2 refusal on a set hash that is not the hash of record")
            con = sqlite3.connect(os.path.join(r, X12, "canary_baseline_pass2.db")); con.execute("ALTER TABLE verdicts ADD COLUMN extra TEXT"); con.commit(); con.close()
            refused = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(cfg, r, pool_check=False)
            except SystemExit as e: refused = "[R1] REFUSED: the two schemas differ" in str(e)
            check(refused, "R1 refusal on a schema difference outside {provider1, provider2}")
            base = [("match_id", "INTEGER"), ("vote1", "TEXT"), ("vote2_raw", "TEXT")]
            prov = [("provider1", "TEXT"), ("provider2", "TEXT")]
            ok_, why_ = schema_check(base, base + prov)
            check(ok_ and "provider1" in why_, "schema_check: provider columns absent from pass 1 only -> accepted, excluded columns printed (%s)" % why_)
            check(schema_check(base + prov, base + prov)[0], "schema_check: identical schemas (exempt columns in both) accepted")
            check(not schema_check([base[1], base[0], base[2]], base + prov)[0], "schema_check: the same columns in a different ORDER -> refused")
            check(not schema_check([("match_id", "INTEGER"), ("vote1", "INTEGER"), ("vote2_raw", "TEXT")], base + prov)[0],
                  "schema_check: a changed declared TYPE -> refused")
            check(not schema_check(base + prov, base)[0], "schema_check: provider columns absent from PASS 2 (present in pass 1) -> refused")
            r = os.path.join(tmp, "r2b"); os.makedirs(r); cfg, cc = _fixture(r, False, 3)
            con = sqlite3.connect(os.path.join(r, X12, "canary_baseline_pass1.db"))
            con.execute("UPDATE verdicts SET winner = CASE WHEN winner='TIE' THEN model_a ELSE 'TIE' END WHERE match_id = 5000"); con.commit(); con.close()
            refused = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(cfg, r, pool_check=False)
            except SystemExit as e: refused = "not the canary's aggregation" in str(e)
            check(refused, "R2 frame refusal: a stored winner that is not the canary's aggregation of the two votes")
            # write-once
            r = os.path.join(tmp, "iid"); cfg, _ = _fixture(os.path.join(tmp, "wo"), False, 3)
            refused = False
            try:
                with contextlib.redirect_stdout(io.StringIO()): analyze(dict(cfg), os.path.join(tmp, "iid"), pool_check=False)
            except SystemExit as e: refused = "WRITE-ONCE" in str(e)
            check(refused, "a second run on an existing outcome is REFUSED (write-once)")
            # the region function: the registered T = 59 region (exact) and a T with a LOWER region (its print branch)
            bad_T = []
            for Tt in range(10, 160, 3):
                pm = null_exact(300, Tt); u_, l_ = region(pm)
                if u_ is None or not (sum(pm[u_:]) <= 0.025 < sum(pm[u_ - 1:])): bad_T.append(Tt)
                if l_ is not None and not (sum(pm[:l_ + 1]) <= 0.025 < sum(pm[:l_ + 2])): bad_T.append(Tt)
            check(not bad_T, "region(): over T = 10..157 each tail is the LARGEST region with P0 <= 0.025 (two-sided alpha 0.05), off at %s" % bad_T)
            up, lo = region(null_exact(300, 59))
            check(up == 7 and lo is None, "T = 59, M = 300 (closed form): upper region n2 >= %s, lower %s (registered: n2 >= 7, none)" % (up, lo))
            v, L, _ = c1_lines("  X", 300, 150, 10, 20_000, 42)
            check(any("a lower region exists" in l for l in L) and v == "FAILED", "a T with a lower region prints that branch and n2 far below E0 reads FAILED")
            # predictions: both branches of each
            P = score_predictions(10, 39, "FAILED", 0.0001, 0.25, 0.95)
            check([r for _, r, _ in P] == ["HELD"] * 5, "P1-P5 HELD branch: " + " | ".join(l for _, _, l in P))
            P = score_predictions(3, 53, "HELD", 0.3, 2.0, 0.5)
            check([r for _, r, _ in P] == ["FAILED"] * 5, "P1-P5 FAILED branch: " + " | ".join(l for _, _, l in P))
            check(len(consequence_lines("HELD")) == 2 and len(consequence_lines("FAILED")) == 2 and consequence_lines("HELD") != consequence_lines("FAILED"),
                  "falsifier / consequence: both branches produce their own lines")
            check(c1_verdict(7, 7, None) == "FAILED" and c1_verdict(6, 7, None) == "HELD" and c1_verdict(0, 7, 0) == "FAILED",
                  "c1_verdict: the region's edges (7 inside, 6 outside, a lower region honoured)")
    except (Exception, SystemExit) as e:      # a refusal inside the selftest is a FAIL line, not an abort
        import traceback
        lines.append("  [FAIL] exception: %r\n%s" % (e, traceback.format_exc())); ok = False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=== %s --selftest (synthetic cache pairs under tempfile.mkdtemp(); no DB of record) ===" % TEST)
    print("\n".join(lines))
    print("SELFTEST %s: %d checks, %d failed" % ("PASS" if ok else "FAIL", len(lines), sum(1 for l in lines if "[FAIL]" in l)))
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="TIE-MECHANICS (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true"); g.add_argument("--dry-run", action="store_true"); g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.selftest: sys.exit(0 if selftest() else 1)
    if a.dry_run: sys.exit(dry_run())
    analyze()
