"""PLACEMENT-CEILING - is the newcomer band at 400 matches a key-tie band or a budget band? (zero calls)
Registered 2026-09-18 in docs/judge_v2_program.md ("Registered 2026-09-18 (before any code or call) - PLACEMENT-CEILING",
commit 3d4536e; plan docs/agents/plans/2026-09-17_continual_capability_profile_leads.md A6; lens arena_profile.md L5;
decides whether C6 PLACEMENT-CURVE is worth its 3,200 calls).

  python tools/analysis/placement_ceiling.py --selftest            (synthetic placement with planted components; opens no DB)
  python tools/analysis/placement_ceiling.py --dry-run             (pool id, cache row counts, the newcomers, the anchors, the
                                                                    key tiers recomputed and ASSERTED = 1..7 / 4..6; no outcome number)
  python tools/analysis/placement_ceiling.py --run [--draws 300]   (write-once: placement_ceiling_outcome.txt + _bands.csv + _curve.csv)

QUESTION (the registration). NEWCOMER-PLACEMENT-LIVE (1,600 calls) placed two real newcomers by four-anchor bisection at
100 pool questions per anchor and FAILED the registered <= 2-tier criterion for both: claude-3-5-sonnet-20241022 banded to
key tiers 1..7 (7 tiers; own tier 3 contained), gpt-4o-mini to 4..6 (3 tiers; own tier 6 contained). Its reading, unmeasured,
was that the width comes from where the bisection lands, not from judge error. Claim under test: the band is a KEY-TIE band
(positions the key itself cannot order at the 0.017 gap, or inside the frontier band), not a BUDGET band (positions the arena
could have separated with more matches). If budget is the band, C6 PLACEMENT-CURVE is worth registering; if not, it is
declined at zero calls and 400 matches stays "not a placement budget" for a structural reason.

HYGIENE. experiment_results/x12_crossdomain/newcomer_placement.db is the single source of verdicts (basename asserted; row
counts printed: per newcomer 4 anchors x 100 questions = 400 question-pairs, each judged in both orders = 800 verdict rows,
1,600 rows in all, 1 unusable content_filter row counted in the denominator); opened mode=ro; pool p2dca21ab5f4ef3ae verified
by pool_guard.assert_pool_of_record as the first printed line; key tiers recomputed from eval_results (mode=ro; roster
printed, Meta-Llama-3-70B-Instruct excluded) exactly as newcomer_placement.analyze did (x20_replications.key_tiers at the
0.017 gap over the x20-judged questions of the 20-model board of record, the board's two caches opened read-only) and
ASSERTED equal to the recorded intervals 1..7 and 4..6 and own tiers 3 and 6 before any decomposition runs (a mismatch refuses
the run). Single-source per-anchor win share with ties 1/2 (the D5 PRIMARY readout), never the mixed fit. Both conventions
printed. A pool reader: runs only outside the night chain (window W2), never beside a construction or a site null (rule 7).

INSTRUMENT.
 (a) Band of newcomer m = the incumbents of the 19-model board lying, in key order, in the key tiers lo_t..hi_t of the
     recorded certificate (lo_t = the tier of the lowest anchor m is certified below, hi_t = the tier of the highest anchor
     m is certified above; the interval newcomer_placement.analyze recorded), the unseparated anchors included; width = the
     number of tiers = hi_t - lo_t + 1 (recorded 7 and 3). The interval is read INCLUSIVE of the bounding anchors' tiers:
     that is the only reading under which the width equals the recorded 7 / 3 the registration asserts (a certificate against
     one member of a tier does not exclude the tier).
 (b) Decomposition, per band incumbent, into exactly one of: (i) KEY-TIE: |key(incumbent) - key(newcomer)| < 0.017 on the
     key the tiers are built on (pool-wide accuracy printed beside, a disagreement flagged); (ii) FRONTIER: member of the
     band FRONTIER-FIT refuses to order (frontier_fit.FRONTIER, asserted against its source) and not (i); (iii) SEPARABLE:
     neither, split into (iii-a) a judged anchor left UNSEPARATED at 100 questions, (iii-b) an incumbent never judged
     against (a further bisection step would be needed; the D5-excluded peer newcomer flagged), and (iii-c) a judged anchor
     CERTIFIED at 100 questions that bounds the band (in the band only by the inclusive tier convention; the registration's
     (iii-a)/(iii-b) split is not exhaustive for it, so it is named rather than dropped). Tier attribution: the component
     of the majority of the tier's band members, ties to the worse component ((iii) worst, then (ii), then (i)), so that
     (i) + (ii) + (iii) = the band width exactly (C1), asserted under every convention.
 (c) Resolution curve: the SAME four anchors, question-stratified subsamples of 25 / 50 / 75 / 100 questions per anchor
     (= 100 / 200 / 300 / 400 question-pairs per newcomer), B >= 300 draws at each size, seed 42; per draw the per-anchor
     certified / unseparated status on the recorded rule (question-clustered bootstrap, 2,000 inner draws, 0.975) and the
     band width in tiers; the curve = median width and [p5, p95] over draws; 100 per anchor = the recorded 7 / 3 by identity
     (the recorded RNG sequence is replayed once and the interval asserted).
 (d) Power column, descriptive: for every unseparated anchor (the (iii-a) ones and, labelled, the (i)/(ii) ones), the number
     of question-pairs at which the observed win share would certify at 0.975 if it held, SE scaled by sqrt(100 / n) from the
     recorded bootstrap SD.
CONVENTIONS. PRIMARY = the recorded rule (ties 1/2, unusable rows excluded); A = ties 1/2 and the unusable row counted 1/2 in
the denominator (the registration's "counted in the denominator"); B = committed verdicts only (ties and unusable dropped).
Only the judged status of an anchor can move between conventions; (i) and (ii) never do.
CRITERIA (HELD / FAILED). C1 the decomposition sums to 7 / 3 under both conventions with the incumbent list per component;
C2 the curve at 100 / 200 / 300 / 400 question-pairs with [p5, p95] over B >= 300 draws and the power column.
PREDICTIONS (blind, labelled). P1 sonnet (iii) = 0 tiers; P2 gpt-4o-mini tier 6 -> (i), tiers 4 and 5 each -> (ii) or (iii);
P3 median width at 100 minus median width at 400 <= 1 tier for both; registrar's addition: at 100 question-pairs sonnet's
width reaches the full span in fewer than half the draws.
FALSIFIER. (iii) >= 2 tiers for either newcomer: budget IS the band there and C6 PLACEMENT-CURVE becomes worth registering.
OUTPUTS (write-once). experiment_results/x12_crossdomain/placement_ceiling_outcome.txt, placement_ceiling_bands.csv (one row
per band incumbent per convention), placement_ceiling_curve.csv (one row per newcomer, size, draw).
"""
import os, sys, re, csv, math, random, sqlite3, argparse, hashlib, statistics
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)

POOL_ID = "p2dca21ab5f4ef3ae"
NEWCOMERS = ["claude-3-5-sonnet-20241022", "gpt-4o-mini"]
EXCLUDED = "Meta-Llama-3-70B-Instruct"
KEY_GAP = 0.017
CONF = 0.975
INNER = 2000            # FRAMEWORK L85: B >= 2,000 when a tail is published at 0.975 (the recorded certificate's B)
SEED = 42
SIZES = (25, 50, 75, 100)
N_ANCHORS, PER_ANCHOR = 4, 100
FRONTIER_FIT_BAND = ("arx_0314", "iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06")   # frontier_fit.py FRONTIER
RECORDED = {"claude-3-5-sonnet-20241022": (1, 7, 3), "gpt-4o-mini": (4, 6, 6)}                # (lo tier, hi tier, own tier), 1-based
COMP_ORDER = ("iii", "ii", "i")     # worst first: the tie-break of the tier attribution
CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "newcomer_placement.db")
OUT_DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
OUT = os.path.join(OUT_DIR, "placement_ceiling_outcome.txt")
OUT_BANDS = os.path.join(OUT_DIR, "placement_ceiling_bands.csv")
OUT_CURVE = os.path.join(OUT_DIR, "placement_ceiling_curve.csv")
SCRIPT_SHA = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()[:16]


# ---------------------------------------------------------------- the recorded rule (newcomer_placement.analyze, replayed)

def q_bootstrap_replay(items, draws, rng):
    """newcomer_placement.q_bootstrap with stat = mean, same RNG consumption: the recorded certificate's draws."""
    qs = sorted(items); out = []
    for _ in range(draws):
        pick = [qs[rng.randrange(len(qs))] for _ in qs]
        vs = [v for q in pick for v in items[q]]
        out.append(sum(vs) / len(vs))
    return out


def status_from_counts(n_up, n_dn, draws, conf=CONF):
    if n_up / draws >= conf: return "below"      # anchor certified BELOW the newcomer (newcomer above)
    if n_dn / draws >= conf: return "above"      # anchor certified ABOVE the newcomer
    return "unseparated"


def certify_replay(items, draws, rng):
    bs = q_bootstrap_replay(items, draws, rng)
    n_up = sum(1 for b in bs if b > 0.5); n_dn = sum(1 for b in bs if b < 0.5)
    n = sum(len(v) for v in items.values()); share = sum(sum(v) for v in items.values()) / n
    sd = statistics.pstdev(bs)
    return share, n, n_up, n_dn, sd, status_from_counts(n_up, n_dn, draws)


def certify_fast(vals2, draws, rng):
    """vals2: int array of 2 x value (0, 1, 2), one entry per usable question; numpy question bootstrap on exact sums."""
    import numpy as np
    m = len(vals2)
    idx = rng.integers(0, m, size=(draws, m))
    s2 = vals2[idx].sum(axis=1)
    n_up = int((s2 > m).sum()); n_dn = int((s2 < m).sum())
    return status_from_counts(n_up, n_dn, draws), n_up, n_dn


def key_tiers(acc, models, gap=KEY_GAP):
    """x20_replications.key_tiers verbatim (asserted equal to it in load_record) so the selftest opens no DB."""
    o = sorted(models, key=lambda m: -acc[m]); out = []; cur = [o[0]]
    for a, b in zip(o, o[1:]):
        if acc[a] - acc[b] < gap: cur.append(b)
        else: out.append(cur); cur = [b]
    out.append(cur); return out


def tier_interval(statuses, tier_of, n_tiers):
    """statuses: {anchor: 'above'|'below'|'unseparated'} -> (lo_t, hi_t, width or None) 0-based, as newcomer_placement did."""
    lo_t = max((tier_of[a] for a, s in statuses.items() if s == "above"), default=0)
    hi_t = min((tier_of[a] for a, s in statuses.items() if s == "below"), default=n_tiers - 1)
    return lo_t, hi_t, (hi_t - lo_t + 1 if lo_t <= hi_t else None)


# ---------------------------------------------------------------- the decomposition (pure; the selftest plants into it)

def component_of(inc, new, acc, frontier, statuses, judged, peer=None, gap=KEY_GAP):
    """(component, sub, note) for one band incumbent. statuses: judged anchor -> status; judged: set of judged anchors."""
    if abs(acc[inc] - acc[new]) < gap: return "i", "i", "KEY-TIE |dkey| %.3f < %.3f" % (abs(acc[inc] - acc[new]), gap)
    if inc in frontier: return "ii", "ii", "FRONTIER-FIT band member"
    if inc in judged:
        s = statuses[inc]
        if s == "unseparated": return "iii", "iii-a", "judged, UNSEPARATED at 100"
        return "iii", "iii-c", "judged, CERTIFIED %s the newcomer at 100 (bounds the band)" % s.upper()
    return "iii", "iii-b", "never judged against" + (" (the peer newcomer: excluded from the anchor set by D5)" if inc == peer else "")


def attribute_tiers(band, comp, tier_of):
    """tier -> component by majority of the tier's band members, ties to the worse component (COMP_ORDER)."""
    by_t = defaultdict(list)
    for m in band: by_t[tier_of[m]].append(comp[m])
    out = {}
    for t, cs in by_t.items():
        cnt = {c: cs.count(c) for c in COMP_ORDER}
        best = max(cnt.values())
        out[t] = next(c for c in COMP_ORDER if cnt[c] == best)      # first in worst-first order among the maxima
    return out


def decompose(new, kt, tier_of, acc, frontier, statuses, judged, lo_t, hi_t, peer=None):
    """Band incumbents = every board model other than the newcomer in tiers lo_t..hi_t. Returns (band, comp, sub, note, tier_comp)."""
    band = [m for t in range(lo_t, hi_t + 1) for m in kt[t] if m != new]
    comp, sub, note = {}, {}, {}
    for m in band: comp[m], sub[m], note[m] = component_of(m, new, acc, frontier, statuses, judged, peer)
    tier_comp = attribute_tiers(band, comp, tier_of)
    assert set(tier_comp) == set(range(lo_t, hi_t + 1)), "every band tier must hold a band incumbent"
    return band, comp, sub, note, tier_comp


def tier_counts(tier_comp):
    return {c: sum(1 for v in tier_comp.values() if v == c) for c in ("i", "ii", "iii")}


def power_pairs(share, sd100, n100=100, z=1.959963984540054):
    """question-pairs at which the observed share would certify at 0.975 if it held: SE_n = sd100 * sqrt(n100 / n)."""
    d = abs(share - 0.5)
    if d == 0 or sd100 == 0: return None
    return int(math.ceil(n100 * (z * sd100 / d) ** 2))


# ---------------------------------------------------------------- data of record

def frontier_band_of_record():
    src = open(os.path.join(HERE, "frontier_fit.py"), encoding="utf-8").read()
    m = re.search(r'^FRONTIER = \((.*?)\)\s*$', src, re.M)
    assert m, "frontier_fit.py no longer defines FRONTIER = (...)"
    got = tuple(s.strip().strip('"') for s in m.group(1).split(",") if s.strip())
    assert got == FRONTIER_FIT_BAND, "FRONTIER-FIT's band drifted: %s vs %s" % (got, FRONTIER_FIT_BAND)
    return got


def open_ro(path):
    assert os.path.exists(path), "missing %s" % path
    return sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)


def load_record():
    """The board of record (both caches read-only, newcomer_placement.board_of_record), the key over its judged questions
    (newcomer_placement.analyze L559-566), the pool-wide key, the tiers, the placement cache rows."""
    import newcomer_placement as npl
    import x20_replications as xr
    import rejudge_grok as rj
    assert os.path.basename(CACHE) == "newcomer_placement.db", CACHE
    assert npl.CACHE == CACHE, "newcomer_placement.py's cache path drifted: %s" % npl.CACHE
    assert xr.KEY_GAP == KEY_GAP
    rows, models, n12, n20 = npl.board_of_record()
    qs_judged = sorted({r[2] for r in rows})
    ev = open_ro(rj.EVAL_DB)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL_ID,))}
    assert pool, "pool of record %s not recorded in reserved_pool" % POOL_ID
    roster = {m for (m,) in ev.execute("SELECT DISTINCT model_name FROM eval_results")}
    Kall = defaultdict(dict)
    for q, m, c in ev.execute("SELECT question_id, model_name, is_correct FROM eval_results"):
        if m in models: Kall[q][m] = int(c or 0)
    ev.close()
    acc = {m: sum(Kall[q][m] for q in qs_judged if m in Kall.get(q, {})) / max(1, sum(1 for q in qs_judged if m in Kall.get(q, {}))) for m in models}
    acc_pool = {m: sum(Kall[q][m] for q in pool if m in Kall.get(q, {})) / max(1, sum(1 for q in pool if m in Kall.get(q, {}))) for m in models}
    kt = xr.key_tiers(acc, models); tier_of = {m: i for i, t in enumerate(kt) for m in t}
    assert kt == key_tiers(acc, models), "local key_tiers drifted from x20_replications.key_tiers"
    con = open_ro(CACHE)
    meta = dict(con.execute("SELECT key, value FROM meta"))
    counts = {"schedule": con.execute("SELECT COUNT(*) FROM schedule").fetchone()[0],
              "verdicts": con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0],
              "invalid": con.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1").fetchone()[0],
              "finish": dict(con.execute("SELECT COALESCE(finish,'(none)'), COUNT(*) FROM verdicts GROUP BY 1"))}
    place = {}
    for new in NEWCOMERS:
        sched = con.execute("SELECT mid, step, opponent, qid FROM schedule WHERE newcomer=? ORDER BY mid", (new,)).fetchall()
        by_step = defaultdict(list)
        for m, step, opp, q in sched: by_step[step].append((m, opp, q))
        steps = []
        for step in sorted(by_step):
            opp = by_step[step][0][1]
            dv = npl.dual_verdicts(con, [m for m, _, _ in by_step[step]], new, opp)
            vals = {}
            for m, _, q in by_step[step]:
                v = dv[m]
                assert v != "PENDING", "pending verdict %d: the cache is not complete" % m
                vals[q] = None if v is None else (1.0 if v == new else (0.5 if v == "TIE" else 0.0))
            steps.append((step, opp, vals))
        srows = con.execute("SELECT step, opponent, lo, hi, wins, losses, ties, unusable, direction FROM steps WHERE newcomer=? ORDER BY step", (new,)).fetchall()
        order, th, inc = npl.incumbent_order(rows, models, new)
        place[new] = {"steps": steps, "steps_rows": srows, "n_sched": len(sched), "order": order}
    con.close()
    return dict(rows=rows, models=models, n12=n12, n20=n20, qs_judged=qs_judged, pool=pool, roster=roster,
                acc=acc, acc_pool=acc_pool, kt=kt, tier_of=tier_of, meta=meta, counts=counts, place=place)


def convention_items(vals, conv):
    """{qid: [value]} for one anchor under a convention. PRIMARY: unusable excluded; A: unusable = 1/2; B: committed only."""
    items = {}
    for q, v in vals.items():
        if v is None:
            if conv == "A": items[q] = [0.5]
            continue
        if conv == "B" and v == 0.5: continue
        items[q] = [v]
    return items


def certificates(new, steps, tier_of, n_tiers, conv):
    """The recorded rule replayed: random.Random(SEED) once per newcomer, anchors in step order, B = INNER."""
    rng = random.Random(SEED)
    out = []; statuses = {}
    for step, opp, vals in steps:
        items = convention_items(vals, conv)
        share, n, n_up, n_dn, sd, st = certify_replay(items, INNER, rng)
        statuses[opp] = st
        out.append(dict(step=step, anchor=opp, n=n, share=share, n_up=n_up, n_dn=n_dn, sd=sd, status=st))
    lo_t, hi_t, width = tier_interval(statuses, tier_of, n_tiers)
    return out, statuses, lo_t, hi_t, width


def assert_recorded(new, lo_t, hi_t, own_t):
    lo_r, hi_r, own_r = RECORDED[new]
    assert (lo_t + 1, hi_t + 1, own_t + 1) == (lo_r, hi_r, own_r), \
        "%s: recomputed key-tier interval %d..%d (own %d) is not the recorded %d..%d (own %d): REFUSED" % (new, lo_t + 1, hi_t + 1, own_t + 1, lo_r, hi_r, own_r)


# ---------------------------------------------------------------- the resolution curve

def curve_for(new, ni, steps, tier_of, n_tiers, draws, sizes=SIZES, inner=INNER, log=None):
    """[(size, draw, width|None, nA, nB, nU)] on the PRIMARY convention; size = questions per anchor."""
    import numpy as np
    per = [(opp, sorted(vals)) for _, opp, vals in steps]
    vals_of = [ {q: v for q, v in vals.items()} for _, _, vals in steps ]
    out = []
    for size in sizes:
        for d in range(draws):
            rng = np.random.default_rng([SEED, ni, size, d])
            statuses = {}
            for k, (opp, qs) in enumerate(per):
                pick = rng.choice(len(qs), size=min(size, len(qs)), replace=False)
                v2 = np.array([int(2 * vals_of[k][qs[i]]) for i in pick if vals_of[k][qs[i]] is not None], dtype=np.int64)
                statuses[opp] = certify_fast(v2, inner, rng)[0] if len(v2) else "unseparated"
            lo_t, hi_t, width = tier_interval(statuses, tier_of, n_tiers)
            nA = sum(1 for s in statuses.values() if s == "above"); nB = sum(1 for s in statuses.values() if s == "below")
            out.append((size, d, width, nA, nB, N_ANCHORS - nA - nB))
        if log: log("  %s: size %d done (%d draws)" % (new, size, draws))
    return out


def summarize_curve(rows):
    """size -> (median, p5, p95, n_draws, n_contradicted, n_fullspan) over draws with a width; p5/p95 by nearest-rank."""
    by = defaultdict(list); contra = defaultdict(int)
    for size, d, w, *_ in rows:
        if w is None: contra[size] += 1
        else: by[size].append(w)
    out = {}
    for size in sorted(set(by) | set(contra)):
        ws = sorted(by[size])
        if not ws: out[size] = (None, None, None, 0, contra[size], 0); continue
        p = lambda f: ws[min(len(ws) - 1, max(0, int(math.ceil(f * len(ws))) - 1))]
        out[size] = (statistics.median(ws), p(0.05), p(0.95), len(ws), contra[size], None)
    return out


# ---------------------------------------------------------------- readout

def readout(R, draws, log):
    kt, tier_of, acc, acc_pool = R["kt"], R["tier_of"], R["acc"], R["acc_pool"]
    n_tiers = len(kt); frontier = frontier_band_of_record()
    L = ["=== PLACEMENT-CEILING: is the newcomer band at 400 matches a key-tie band or a budget band? (0 calls) ===",
         "  pool %s | cache %s (mode=ro; producing script sha %s, this script %s) | judge %s | max_tokens %s | temperature %s | reference %s"
         % (POOL_ID, os.path.relpath(CACHE, ROOT), R["meta"].get("script_sha256_16"), SCRIPT_SHA, R["meta"].get("judge_model"),
            R["meta"].get("max_tokens"), R["meta"].get("temperature"), R["meta"].get("reference")),
         "  cache rows: schedule %d | verdicts %d (invalid %d; finish_reason %s) = %d newcomers x %d anchors x %d questions x 2 orders"
         % (R["counts"]["schedule"], R["counts"]["verdicts"], R["counts"]["invalid"], R["counts"]["finish"], len(NEWCOMERS), N_ANCHORS, PER_ANCHOR),
         "  board of record: x12 %d + x20 %d = %d verdicts, %d models, %s absent; key = eval_results is_correct over the %d x20-judged questions (the tier key), pool-wide key over %d pool questions printed beside; eval_results roster %d models (%d with %s excluded)"
         % (R["n12"], R["n20"], len(R["rows"]), len(R["models"]), EXCLUDED, len(R["qs_judged"]), len(R["pool"]), len(R["roster"]), len(R["roster"] - {EXCLUDED}), EXCLUDED),
         "  key tiers at %.3f gap: %d%s" % (KEY_GAP, n_tiers, "" if n_tiers == 14 else " (MISMATCH: the record says 14)")]
    for i, t in enumerate(kt): L.append("    tier %2d: %s" % (i + 1, ", ".join("%s %.3f (pool %.3f)" % (m, acc[m], acc_pool[m]) for m in t)))
    L.append("  frontier band read from FRONTIER-FIT (frontier_fit.FRONTIER, membership only, nothing inside it ordered): %s" % ", ".join(frontier))
    L.append("  conventions: PRIMARY = ties 1/2, unusable excluded (the recorded rule); A = ties 1/2, unusable 1/2 in the denominator; B = committed verdicts only")
    assert R["counts"]["schedule"] == len(NEWCOMERS) * N_ANCHORS * PER_ANCHOR and R["counts"]["verdicts"] == 2 * R["counts"]["schedule"], "cache is not the complete 1,600-row run"
    bands_csv = []; curve_csv = []; verdict = {}; curves = {}
    for ni, new in enumerate(NEWCOMERS):
        P = R["place"][new]; peer = [n for n in NEWCOMERS if n != new][0]
        assert P["n_sched"] == N_ANCHORS * PER_ANCHOR, "%s: %d scheduled" % (new, P["n_sched"])
        L.append(""); L.append("--- %s (own key tier %d, key %.3f, pool key %.3f) ---" % (new, tier_of[new] + 1, acc[new], acc_pool[new]))
        for step, opp, lo, hi, w, l, t, u, d in P["steps_rows"]:
            L.append("  step %d [%2d,%2d] vs %-30s %3d : %3d (ties %2d, unusable %2d) -> %s (steps row of record)" % (step, lo, hi, opp, w, l, t, u, d))
        judged = {opp for _, opp, _ in P["steps"]}
        per_conv = {}
        for conv in ("PRIMARY", "A", "B"):
            certs, statuses, lo_t, hi_t, width = certificates(new, P["steps"], tier_of, n_tiers, conv)
            per_conv[conv] = (certs, statuses, lo_t, hi_t, width)
            L.append("  [%s] per-anchor certificate, win share, question-clustered bootstrap B=%d, seed %d replayed in step order:" % (conv, INNER, SEED))
            for c in certs:
                L.append("    step %d vs %-30s (key tier %2d, key %.3f): n %3d, share %.3f, sd %.3f | draws above 0.5: %d, below: %d | %s at %.3f"
                         % (c["step"], c["anchor"], tier_of[c["anchor"]] + 1, acc[c["anchor"]], c["n"], c["share"], c["sd"], c["n_up"], c["n_dn"],
                            {"above": "anchor ABOVE newcomer", "below": "newcomer ABOVE anchor", "unseparated": "UNSEPARATED"}[c["status"]], CONF))
            L.append("    key-tier interval: %s" % ("KEY-CONTRADICTED" if width is None else "tiers %d..%d (%d tiers)" % (lo_t + 1, hi_t + 1, width)))
        certs, statuses, lo_t, hi_t, width = per_conv["PRIMARY"]
        assert_recorded(new, lo_t, hi_t, tier_of[new])
        L.append("  ASSERTED: PRIMARY interval %d..%d, own tier %d = the recorded %d..%d / %d: OK" % (lo_t + 1, hi_t + 1, tier_of[new] + 1, *RECORDED[new]))
        # ---- (b) decomposition, on the band of record (the PRIMARY interval), under every convention
        c1 = {}
        for conv in ("PRIMARY", "A", "B"):
            statuses_c = per_conv[conv][1]
            band, comp, sub, note, tier_comp = decompose(new, kt, tier_of, acc, frontier, statuses_c, judged, lo_t, hi_t, peer)
            tc = tier_counts(tier_comp); c1[conv] = (tc, tier_comp, band, comp, sub)
            L.append("  [%s] decomposition of the band (tiers %d..%d, %d incumbents):" % (conv, lo_t + 1, hi_t + 1, len(band)))
            for m in band:
                flag = "" if (abs(acc_pool[m] - acc_pool[new]) < KEY_GAP) == (comp[m] == "i") else "   <- (i) would differ on the pool-wide key (|d| %.3f)" % abs(acc_pool[m] - acc_pool[new])
                L.append("    tier %2d %-30s key %.3f (pool %.3f)  %-5s %s%s" % (tier_of[m] + 1, m, acc[m], acc_pool[m], "(" + sub[m] + ")", note[m], flag))
                bands_csv.append(dict(newcomer=new, convention=conv, tier=tier_of[m] + 1, incumbent=m, key=round(acc[m], 4), key_pool=round(acc_pool[m], 4),
                                      dkey=round(acc[m] - acc[new], 4), component=comp[m], sub=sub[m], judged_status=statuses_c.get(m, "never judged"), tier_component=tier_comp[tier_of[m]]))
            L.append("    tier attribution (majority; ties to the worse, (iii) > (ii) > (i)): %s" % ", ".join("tier %d -> (%s)" % (t + 1, tier_comp[t]) for t in sorted(tier_comp)))
            for c in ("i", "ii", "iii"):
                L.append("    (%s) %d tier%s: incumbents %s" % (c, tc[c], "" if tc[c] == 1 else "s", ", ".join("%s(t%d)" % (m, tier_of[m] + 1) for m in band if comp[m] == c) or "-"))
            L.append("    (iii) split: iii-a %d, iii-b %d, iii-c %d incumbents" % tuple(sum(1 for m in band if sub[m] == s) for s in ("iii-a", "iii-b", "iii-c")))
            ok = tc["i"] + tc["ii"] + tc["iii"] == width
            L.append("    C1 [%s]: (i) %d + (ii) %d + (iii) %d = %d vs band width %d (denominator: the %d band incumbents listed): %s"
                     % (conv, tc["i"], tc["ii"], tc["iii"], sum(tc.values()), width, len(band), "HELD" if ok else "FAILED"))
            assert ok
        # ---- (d) power column
        L.append("  power column (descriptive; unseparated anchors on PRIMARY; SE_n = sd_100 x sqrt(100 / n); certify at %.3f if the share held):" % CONF)
        tcP, _, bandP, compP, subP = c1["PRIMARY"]
        any_uns = False
        for c in certs:
            if c["status"] != "unseparated": continue
            any_uns = True
            npairs = power_pairs(c["share"], c["sd"], c["n"])
            L.append("    vs %-30s (%s) share %.3f sd %.3f n %d -> %s question-pairs" % (c["anchor"], subP.get(c["anchor"], "?"), c["share"], c["sd"], c["n"],
                                                                                          "never (share = 0.5)" if npairs is None else "%d" % npairs))
        if not any_uns: L.append("    no unseparated anchor")
        if not any(subP[m] == "iii-a" for m in bandP): L.append("    (iii-a) anchors: none")
        # ---- (c) resolution curve
        log("curve for %s: %d draws x %d sizes, inner B=%d" % (new, draws, len(SIZES), INNER))
        rows_c = curve_for(new, ni, P["steps"], tier_of, n_tiers, draws, log=log)
        for size, d, w, nA, nB, nU in rows_c:
            curve_csv.append(dict(newcomer=new, questions_per_anchor=size, question_pairs=N_ANCHORS * size, draw=d, width=("" if w is None else w), certified_above=nA, certified_below=nB, unseparated=nU))
        S = summarize_curve(rows_c); curves[new] = S
        full = {size: sum(1 for s_, d_, w, *_ in rows_c if s_ == size and w == n_tiers) for size in SIZES}
        L.append("  C2 resolution curve (same four anchors; %d question-stratified draws per size, seed %d; per draw the recorded rule at B=%d):" % (draws, SEED, INNER))
        for size in SIZES:
            med, p5, p95, n_ok, n_contra, _ = S[size]
            L.append("    %3d q/anchor = %3d question-pairs: median width %s tiers, [p5, p95] = [%s, %s] over %d draws | key-contradicted draws %d | full-span (%d-tier) draws %d (%.3f)"
                     % (size, N_ANCHORS * size, "%g" % med if med is not None else None, p5, p95, n_ok, n_contra, n_tiers, full[size], full[size] / draws))
        # identity at 100: every draw is the same 100 questions; the recorded certificate was asserted above
        L.append("    400 question-pairs = the recorded %d tiers by identity (PRIMARY interval asserted above; the draws at 100 differ only by the inner bootstrap's RNG)" % width)
        verdict[new] = dict(tc=c1["PRIMARY"][0], tcA=c1["A"][0], tcB=c1["B"][0], width=width, S=S, full100=full[25] / draws, tier_comp=c1["PRIMARY"][1])
    # ---- predictions and the falsifier
    L.append(""); L.append("=== criteria, predictions (blind, labelled) and the falsifier ===")
    v_s, v_g = verdict[NEWCOMERS[0]], verdict[NEWCOMERS[1]]
    L.append("  C1 HELD under PRIMARY, A and B for both newcomers (asserted above)")
    L.append("  C2 the curve at 100 / 200 / 300 / 400 question-pairs with [p5, p95] over %d draws (>= 300 required) and the power column, printed above -> %s" % (draws, "HELD" if draws >= 300 else "FAILED (draws < 300)"))
    p1 = v_s["tc"]["iii"] == 0
    L.append("  P1 sonnet's width entirely (i) + (ii), (iii) = 0 tiers: (i) %d + (ii) %d + (iii) %d -> %s" % (v_s["tc"]["i"], v_s["tc"]["ii"], v_s["tc"]["iii"], "HELD" if p1 else "FAILED"))
    tcg = v_g["tier_comp"]; t6 = tcg.get(5); t4 = tcg.get(3); t5 = tcg.get(4)
    p2 = t6 == "i" and t4 in ("ii", "iii") and t5 in ("ii", "iii")
    L.append("  P2 gpt-4o-mini: tier 6 -> (i), tiers 4 and 5 -> (ii) or (iii): tier 4 (%s), tier 5 (%s), tier 6 (%s) -> %s" % (t4, t5, t6, "HELD" if p2 else "FAILED"))
    p3s = []
    for new in NEWCOMERS:
        S = verdict[new]["S"]; m100, m400 = S[25][0], S[100][0]
        ok = m100 is not None and m400 is not None and (m100 - m400) <= 1
        p3s.append(ok); L.append("  P3 %s: median width at 100 question-pairs %s minus at 400 %s = %s <= 1 -> %s" % (new, "%g" % m100 if m100 is not None else None, "%g" % m400 if m400 is not None else None, "%g" % (m100 - m400) if m100 is not None and m400 is not None else None, "HELD" if ok else "FAILED"))
    L.append("  P3 overall: %s" % ("HELD" if all(p3s) else "FAILED"))
    L.append("  registrar's addition: sonnet at 100 question-pairs reaches the full %d-tier span in %.3f of draws (< 0.5: %s)" % (len(kt), v_s["full100"], "HELD" if v_s["full100"] < 0.5 else "FAILED"))
    fired = [new for new in NEWCOMERS if verdict[new]["tc"]["iii"] >= 2]
    L.append("  FALSIFIER (iii) >= 2 tiers for either newcomer (PRIMARY): sonnet (iii) %d, gpt-4o-mini (iii) %d -> %s"
             % (v_s["tc"]["iii"], v_g["tc"]["iii"], "FIRED for %s: budget IS the band there; C6 PLACEMENT-CURVE is worth registering (a registration, not a launch)" % ", ".join(fired)
                if fired else "not fired: C6 declined at zero calls; the 400-match band is structural (key ties and the frontier)"))
    for conv in ("A", "B"):
        f = [new for new in NEWCOMERS if verdict[new]["tc" + conv]["iii"] >= 2]
        L.append("    under convention %s: sonnet (iii) %d, gpt-4o-mini (iii) %d -> %s" % (conv, v_s["tc" + conv]["iii"], v_g["tc" + conv]["iii"], "fired for " + ", ".join(f) if f else "not fired"))
    L.append("  not overturned by this test: the FAIL of criterion (22), the two placements' directions, the contained key tiers, the frontier order (nothing inside the band is ordered)")
    return L, bands_csv, curve_csv


# ---------------------------------------------------------------- modes

def log(msg): print("[placement-ceiling] %s" % msg, file=sys.stderr, flush=True)


def dry_run():
    R = load_record()
    frontier = frontier_band_of_record()
    kt, tier_of, acc = R["kt"], R["tier_of"], R["acc"]
    print("cache %s (mode=ro): schedule %d | verdicts %d (invalid %d; finish_reason %s) | meta judge %s cap %s temperature %s reference %s producing sha %s"
          % (os.path.relpath(CACHE, ROOT), R["counts"]["schedule"], R["counts"]["verdicts"], R["counts"]["invalid"], R["counts"]["finish"],
             R["meta"].get("judge_model"), R["meta"].get("max_tokens"), R["meta"].get("temperature"), R["meta"].get("reference"), R["meta"].get("script_sha256_16")))
    print("board of record: x12 %d + x20 %d = %d verdicts, %d models, %s absent | %d x20-judged questions | pool %d questions | eval_results roster %d (%d without %s)"
          % (R["n12"], R["n20"], len(R["rows"]), len(R["models"]), EXCLUDED, len(R["qs_judged"]), len(R["pool"]), len(R["roster"]), len(R["roster"] - {EXCLUDED}), EXCLUDED))
    print("key tiers at %.3f gap over the x20-judged questions: %d (record: 14 -> %s)" % (KEY_GAP, len(kt), "OK" if len(kt) == 14 else "MISMATCH"))
    for i, t in enumerate(kt): print("    tier %2d: %s" % (i + 1, ", ".join("%s %.3f" % (m, acc[m]) for m in t)))
    print("frontier band of record (FRONTIER-FIT, asserted against frontier_fit.py): %s" % ", ".join(frontier))
    for new in NEWCOMERS:
        P = R["place"][new]
        n_us = sum(1 for _, _, vals in P["steps"] for v in vals.values() if v is None)
        print("\n[%s] own key tier %d (key %.3f) | scheduled %d question-pairs = %d verdict rows | unusable %d (counted in the denominator) | peer never an anchor: %s"
              % (new, tier_of[new] + 1, acc[new], P["n_sched"], 2 * P["n_sched"], n_us, [n for n in NEWCOMERS if n != new][0]))
        for step, opp, lo, hi, w, l, t, u, d in P["steps_rows"]:
            print("    step %d [%2d,%2d] anchor %-30s (key tier %2d) %3d : %3d (ties %2d, unusable %2d) -> %s" % (step, lo, hi, opp, tier_of[opp] + 1, w, l, t, u, d))
        certs, statuses, lo_t, hi_t, width = certificates(new, P["steps"], tier_of, len(kt), "PRIMARY")
        assert_recorded(new, lo_t, hi_t, tier_of[new])
        print("    recorded certificate replayed on PRIMARY: interval %d..%d, own tier %d = recorded %d..%d / %d: ASSERTED OK (statuses: %s)"
              % (lo_t + 1, hi_t + 1, tier_of[new] + 1, *RECORDED[new], ", ".join("%s %s" % (a, s) for a, s in statuses.items())))
        band = [m for t in range(lo_t, hi_t + 1) for m in kt[t] if m != new]
        print("    band incumbents (tiers %d..%d, %d): %s" % (lo_t + 1, hi_t + 1, len(band), ", ".join("%s(t%d)" % (m, tier_of[m] + 1) for m in band)))
    print("\ncurve cost: %d newcomers x %d sizes x --draws (>= 300) x %d anchors bootstraps of B=%d (numpy); minutes" % (len(NEWCOMERS), len(SIZES), N_ANCHORS, INNER))
    print("outputs (write-once): %s, %s, %s%s" % (os.path.relpath(OUT, ROOT), os.path.relpath(OUT_BANDS, ROOT), os.path.relpath(OUT_CURVE, ROOT),
                                                  "  (EXISTS: --run would refuse)" if os.path.exists(OUT) else ""))
    print("script sha256[:16] %s" % SCRIPT_SHA)
    print("dry run OK: 0 calls, no outcome number computed, nothing written")


def run(draws):
    assert draws >= 300, "the registration says B >= 300 draws per size"
    for p in (OUT, OUT_BANDS, OUT_CURVE):
        if os.path.exists(p):
            print("REFUSED: %s exists; the outcome of record is written once" % p); sys.exit(5)
    R = load_record()
    L, bands_csv, curve_csv = readout(R, draws, log)
    txt = "\n".join(L); print(txt)
    with open(OUT, "w", encoding="utf-8") as f: f.write(txt + "\n")
    with open(OUT_BANDS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(bands_csv[0].keys())); w.writeheader(); w.writerows(bands_csv)
    with open(OUT_CURVE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(curve_csv[0].keys())); w.writeheader(); w.writerows(curve_csv)
    print("written: %s, %s (%d rows), %s (%d rows)" % (os.path.relpath(OUT, ROOT), os.path.relpath(OUT_BANDS, ROOT), len(bands_csv), os.path.relpath(OUT_CURVE, ROOT), len(curve_csv)))


# ---------------------------------------------------------------- selftest (synthetic; no DB)

def selftest():
    global OUT
    # planted key: 12 models; tiers at the 0.017 gap. Newcomer N key 0.780.
    acc = {"G": 0.912, "A1": 0.833, "I": 0.818, "X3": 0.784, "N": 0.780, "F4": 0.750, "D": 0.651, "M": 0.631, "H": 0.629,
           "Q1": 0.492, "Q2": 0.476, "Z": 0.300}
    models = sorted(acc); kt = key_tiers(acc, models); tier_of = {m: i for i, t in enumerate(kt) for m in t}
    assert [tuple(t) for t in kt] == [("G",), ("A1", "I"), ("X3", "N"), ("F4",), ("D",), ("M", "H"), ("Q1", "Q2"), ("Z",)], kt
    frontier = ("G", "A1", "I", "F4")
    # planted verdicts: anchor G certified above N, F4 unseparated, Q2 certified below, X3 unseparated
    rng = random.Random(7)
    def plant(p_win, n=100):
        return {q: (1.0 if rng.random() < p_win else 0.0) for q in range(1000, 1000 + n)}
    steps = [(1, "Q2", plant(0.90)), (2, "F4", plant(0.50)), (3, "G", plant(0.20)), (4, "X3", plant(0.51))]
    steps[1][2][1003] = None                                      # one unusable row, as the record has
    certs, statuses, lo_t, hi_t, width = certificates("N", steps, tier_of, len(kt), "PRIMARY")
    assert statuses == {"Q2": "below", "F4": "unseparated", "G": "above", "X3": "unseparated"}, statuses
    assert (lo_t, hi_t, width) == (0, 6, 7), (lo_t, hi_t, width)
    band, comp, sub, note, tier_comp = decompose("N", kt, tier_of, acc, frontier, statuses, set(statuses), lo_t, hi_t, peer="M")
    exp = {"G": "ii", "A1": "ii", "I": "ii", "X3": "i", "F4": "ii", "D": "iii-b", "M": "iii-b", "H": "iii-b", "Q1": "iii-b", "Q2": "iii-c"}
    assert {m: sub[m] for m in band} == exp, {m: sub[m] for m in band}
    assert "D5" in note["M"], note["M"]
    tc = tier_counts(tier_comp)
    assert tc == {"i": 1, "ii": 3, "iii": 3} and sum(tc.values()) == width, (tc, width)
    # tie-break: a tier with one (i) and one (iii) goes to (iii); one (i) and one (ii) goes to (ii)
    assert attribute_tiers(["a", "b"], {"a": "i", "b": "iii"}, {"a": 0, "b": 0}) == {0: "iii"}
    assert attribute_tiers(["a", "b"], {"a": "i", "b": "ii"}, {"a": 0, "b": 0}) == {0: "ii"}
    assert attribute_tiers(["a", "b", "c"], {"a": "i", "b": "i", "c": "iii"}, {"a": 0, "b": 0, "c": 0}) == {0: "i"}
    # conventions: A adds the unusable row at 1/2, B drops ties (none planted) -> same statuses here
    for conv in ("A", "B"):
        _, st2, *_ = certificates("N", steps, tier_of, len(kt), conv)
        assert st2 == statuses, (conv, st2)
    # key-contradicted interval
    assert tier_interval({"G": "below", "Q2": "above"}, tier_of, len(kt))[2] is None
    # power column: share 0.51, sd 0.05 -> 100 * (1.96 * 0.05 / 0.01)^2 = 9604
    assert power_pairs(0.51, 0.05) == 9604 and power_pairs(0.5, 0.05) is None
    # the curve machinery at a small B recovers the planted width at full size and widens at 25
    rows = curve_for("N", 0, steps, tier_of, len(kt), draws=8, sizes=(25, 100), inner=400)
    S = summarize_curve(rows)
    assert S[100][0] == 7 and S[100][3] == 8, S
    assert S[25][0] is None or S[25][0] >= 7, S      # fewer questions never narrows a band bounded by certified anchors
    # write-once guard: run() refuses (exit 5) before opening anything when the outcome file exists
    scratch = os.path.join(os.environ.get("TEMP", HERE), "placement_ceiling_selftest_outcome.txt")
    open(scratch, "w").write("x"); saved = OUT; OUT = scratch
    try:
        try: run(300); raise AssertionError("run() did not refuse an existing outcome file")
        except SystemExit as e: assert e.code == 5, e.code
    finally:
        OUT = saved; os.remove(scratch)
    # frontier band of record is readable from the source
    assert frontier_band_of_record() == FRONTIER_FIT_BAND
    print("selftest OK: planted decomposition recovered (%s), tiers %s sum to %d, tie-breaks, conventions, contradiction, power, curve at sizes 25/100" % (tc, dict(sorted(tier_comp.items())), width))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="synthetic placement, opens no DB")
    ap.add_argument("--draws", type=int, default=300, help="subsample draws per size (registration: B >= 300)")
    a = ap.parse_args()
    if a.selftest: selftest(); sys.exit(0)
    import pool_guard
    print("pool of record %s" % pool_guard.assert_pool_of_record(POOL_ID))
    if a.dry_run: dry_run()
    elif a.run: run(a.draws)
    else: ap.print_help()
