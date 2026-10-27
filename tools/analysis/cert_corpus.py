"""CERT-CORPUS — the separation certificate read on the GEN-ARENA cache (FRAMEWORK item 8; zero calls).

  python tools/analysis/cert_corpus.py [--refresh]

REGISTERED BY REFERENCE at commit eaf1dbf (docs/plan_2026-09-15.md); the item's text in docs/design/FRAMEWORK.md
(commit 8d77f7b), "Tests to register before shipping", item 8, quoted verbatim:

    8. CERT-CORPUS. Widener fit and raw miscalibration read on the GEN-ARENA cache after (7). Criterion:
       calibration status by the power rule. Prediction: UNDETERMINED (nominal < 3); product is the widener's
       sign and utility on checker cells. 0 calls.

The power rule (FRAMEWORK, Stage 6, "Calibration statement per board"): called count; wrong count as
all(established); nominal expected wrong calls among called edges, sum(1 - c~); the wrong-direction rate on the
unfiltered edge set with a 95% upper bound; and one status word: UNDETERMINED when nominal < 3; UNDETERMINED
(power: 2x undetectable) when 3 <= nominal < 9, with the smallest ratio the rule could call; NOT DETECTABLY
MISCALIBRATED when nominal >= 9 and Poisson P(>= observed | nominal) > 0.05; MISCALIBRATED otherwise. The word
"calibrated" is never emitted.

WHAT IS READ. The GEN-ARENA cache (experiment_results/multicorpus/gen_arena_grok.db: 3,000 valid verdicts,
grok-4-1-fast-non-reasoning, verifier reference, no rubric, TIE = 0.5 as the board convention of record) on the
8-model roster, and item 7's checker backfill (experiment_results/multicorpus/checker_answers_v1.db, verified
unchanged by item 7's 2026-09-16 re-run). The widener's inputs are exactly Stage 6's: m, s from a question bootstrap
of the cell's board (B = 300, Random(42), the same draw order as systematic_budget.build()); A = answer agreement
over the cell's EVAL-side questions where both models have an extracted answer (MATH: item 7's reading B, checker of
record + NON_TERMINATED -> blank, trimmed case-insensitive string rule on the normalised form; IFEval: identical
per-constraint strict vectors). The key is the checker (MATH: MATH-FIX correctness, IFEval: prompt-level strict).
Wrong-direction counts print as all(established) with established = exact McNemar p < 0.05 on the cell's JUDGED
questions (systematic_budget.mcnemar_edge / established, the committed helpers), and the fit, cbud, craw and nll
are systematic_budget's own.

READINGS TAKEN WHERE THE ITEM IS UNDER-SPECIFIED (each the one hardest on the programme's claims, stated here):
  cells      the two registered GEN-ARENA boards (MATH source row, IFEVAL source row) are the FIT OF RECORD; the
             seven MATH domain cells (a partition of the MATH row) are read beside at build()'s 200-match floor
             and at JUDGE-TRANSFER's registered 100-match floor. The fit never mixes a row with its own sub-cells.
  checker    "checker cells" is measured, not assumed: D_c per cell on THIS roster (eval-side question-pairs with
             two non-blank extracted answers, item 7's reading B, question-bootstrap interval) is printed, and a
             cell below 0.95 is PREDICTIVE-ONLY by Stage 1 and excluded from the product read. Item 7's verdict of
             record (MATH row 0.8268 on the 18-model roster) is a roster property of the two R1 distills, neither
             of which is on the GEN-ARENA roster; the number that governs here is this board's own D_c.
  edges      UNFILTERED: every pair with a non-zero key gap (SYSTEMATIC-BUDGET's correction (b)); the gap >= 0.02
             filter is printed beside, never used for a verdict.
  labels     the widener's sign is read on ESTABLISHED labels (the attack that killed the conformal form), with
             the all-label fit beside; "identified" = profile delta-deviance at b1 = 0 >= 3.84.
  utility    share of ALL unfiltered edges the fitted widener still calls at 0.975 (bar 60%, SYSTEMATIC-BUDGET (2));
             raw calls retained and correct calls surrendered printed beside.
  A          of record over the cell's EVAL-side questions of GEN-ARENA's own split (Stage 6's definition; MATH 397,
             IFEVAL 162); A over the cell's JUDGED questions (MATH 394: three eval-side questions were never drawn)
             and over the union pool of record's eval side (paeec37aa28063c75) are sensitivities. Item 7's readings
             A and B of the extracted answer coincide on this roster (no R1 distill), which the script asserts.
  nominal    for the raw certificate c~ = c_raw, so nominal = sum(1 - c_raw) (empirical, B draws); the Gaussian
             sum(1 - Phi(|m|/s)) that systematic_budget.py prints is read beside. The status word of record is taken
             on the ALL-label wrong count (harder than established); both are printed where they differ.
  x12 cold   the shipped Mistral/MMLU-Pro parameters are stored per (board id, judge_model) and REFUSED elsewhere;
             they are applied here as a labelled diagnostic only, never as a certificate.

KEY DENOMINATOR for every McNemar count: the cell's judged questions in the GEN-ARENA cache (MATH 394, IFEVAL 162;
domain cells 36-92). The GEN-ARENA split is a random.Random(42) re-derivation, NOT the union pool of record; the
overlap with paeec37aa28063c75 is printed.

NO network, NO LLM calls. Output: experiment_results/x12_crossdomain/cert_corpus.txt. Edge tables are cached under
the block-1 scratchpad (--refresh rebuilds). The header carries the sha256 of this file (the producing code hash).
"""
import os, sys, math, json, random, sqlite3, time, argparse, hashlib
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import norm, poisson, beta
import pool_guard
import systematic_budget as sb
import judge_free_tests as jf
import generative_arena as ga

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "cert_corpus.txt")
GEN_ARENA = os.path.join(ROOT, "experiment_results", "multicorpus", "gen_arena_grok.db")
CHECKER_DB = os.path.join(ROOT, "experiment_results", "multicorpus", "checker_answers_v1.db")
CORPUS_DB = os.path.join(ROOT, "multicorpus_cache_v1.db")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Temp", "claude",
                       "Z--FAC-TUBerlin-THESIS-TaxoArena", "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "block1")
CACHE = os.path.join(SCRATCH, "cert_corpus_edges_v2.json")
UNION_POOL = "paeec37aa28063c75"
EXCLUDE = {"Meta-Llama-3-70B-Instruct"}
B = 300              # the certificate fit's bootstrap size of record
B_TAIL = 2000        # FRAMEWORK: B >= 2,000 when publishing a c_raw tail at 0.975 (sensitivity here)
B_DC = 2000          # question bootstrap for the D_c interval (item 7's B)
THRESH = 0.975
GAP = 0.02
DC_BAR = 0.95        # Stage 1: D_c < 0.95 -> PREDICTIVE-ONLY
X12_891 = (-3.2326, 3.3133)      # shipped pair, 891 key-gap-filtered x12 edges (Mistral / MMLU-Pro)
X12_920 = (-3.0438, 3.1980)      # the unfiltered 920-edge refit, pending UNFILTERED-ADOPT
FLOOR_BUILD = 200                # systematic_budget.build()'s anchor floor
FLOOR_JT = 100                   # JUDGE-TRANSFER's registered floor


# ------------------------------------------------------------------------------------------------ data
def load():
    g = sqlite3.connect("file:%s?mode=ro" % GEN_ARENA, uri=True)
    verdicts = [r for r in g.execute("SELECT match_id, source, qid, model_a, model_b, winner, invalid FROM verdicts") if not r[6]]
    n_inv = g.execute("SELECT COUNT(*) FROM verdicts WHERE invalid=1").fetchone()[0]
    sched = g.execute("SELECT match_id, source, qid, model_a, model_b FROM schedule").fetchall()
    roster = sorted(({r[3] for r in verdicts} | {r[4] for r in verdicts}) - EXCLUDE)
    verdicts = [r for r in verdicts if r[3] in roster and r[4] in roster]
    c = sqlite3.connect("file:%s?mode=ro" % CORPUS_DB, uri=True)
    dom = {q: (s, d) for q, s, d in c.execute("SELECT question_id, source, domain FROM corpus_questions WHERE source IN ('MATH','IFEVAL')")}
    pool = {q for (q,) in c.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (UNION_POOL,))}
    active = pool_guard.assert_frozen_pool(c, UNION_POOL)   # the union pool, verified by id on this DB (no active pointer)
    # GEN-ARENA's own split, re-derived from the committed function, so the eval side of THAT split is known;
    # build_schedule() drew from the eval-side questions with full roster coverage
    Q, ga_test = ga.reserved_split(c)
    G_ga = ga.correctness(c)     # the key GEN-ARENA's outcome used (mathfix over ingested)
    ga_eval = {q for q in ga_test if q in dom and all(m in G_ga.get(q, {}) for m in roster)}
    k = sqlite3.connect("file:%s?mode=ro" % CHECKER_DB, uri=True)
    meta = dict(k.execute("SELECT key, value FROM checker_answer_ingest_meta").fetchall())
    XA = defaultdict(dict); XB = defaultdict(dict); K = defaultdict(dict); XC_prompt = defaultdict(dict)
    n_diff = 0
    for q, m, xn, nt, cc, mfc in k.execute("SELECT question_id, model_name, x_norm, non_terminated, checker_correct, mathfix_correct FROM math_checker_answers"):
        if m in EXCLUDE: continue
        K[q][m] = int(cc)
        if mfc is not None and int(mfc) != int(cc): n_diff += 1
        if xn is not None and xn != "":
            XA[q][m] = xn
            if not nt: XB[q][m] = xn
    for q, m, vec, nt, ap, ic in k.execute("SELECT question_id, model_name, strict_vector, non_terminated, all_pass_strict, ingested_is_correct FROM ifeval_checker_answers"):
        if m in EXCLUDE: continue
        K[q][m] = int(ic)
        XA[q][m] = vec
        if not nt: XB[q][m] = vec
        XC_prompt[q][m] = str(int(ap))
    return dict(verdicts=verdicts, n_inv=n_inv, sched=sched, roster=roster, dom=dom, pool=pool, active=active,
                ga_test=ga_test, ga_eval=ga_eval, G_ga=G_ga, XA=XA, XB=XB, K=K, XC_prompt=XC_prompt, n_diff=n_diff, meta=meta)


def cell_of(D, q):
    return "%s/%s" % D["dom"][q]


def eval_qs_for(D, name):
    """GEN-ARENA's own eval-side questions (full roster coverage) belonging to a cell."""
    if name in ("MATH", "IFEVAL"):
        return sorted(q for q in D["ga_eval"] if D["dom"][q][0] == name)
    return sorted(q for q in D["ga_eval"] if cell_of(D, q) == name)


def pool_qs_for(D, name):
    if name in ("MATH", "IFEVAL"):
        return sorted(q for q in D["pool"] if D["dom"].get(q, (None,))[0] == name)
    return sorted(q for q in D["pool"] if D["dom"].get(q) == tuple(name.split("/", 1)))


def agree_rate(qs, X, a, b, source):
    eq = (lambda x, y: x.strip().lower() == y.strip().lower()) if source == "MATH" else (lambda x, y: x == y)
    both = [q for q in qs if X.get(q, {}).get(a) is not None and X.get(q, {}).get(b) is not None]
    if not both: return None, 0
    return sum(1 for q in both if eq(X[q][a], X[q][b])) / len(both), len(both)


def dc_cell(qs, X, roster, seed=42, B_=B_DC):
    """D_c = share of (eval-side question, pair) cells with two non-blank extracted answers; question bootstrap."""
    pairs = [(roster[i], roster[j]) for i in range(len(roster)) for j in range(i + 1, len(roster))]
    per_q = np.array([sum(1 for a, b in pairs if X.get(q, {}).get(a) is not None and X.get(q, {}).get(b) is not None) / len(pairs) for q in qs])
    rng = np.random.default_rng(seed)
    bs = np.array([per_q[rng.integers(0, len(qs), len(qs))].mean() for _ in range(B_)])
    return float(per_q.mean()), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def build_edges(D, cells, B_, seed):
    """cells: list of (name, [verdict rows]). Same loop as systematic_budget.build(): one Random(seed) shared over
    the cells in sorted order, pick = [qs[rng.randrange(len(qs))] for _ in qs], board_from with TIE = 0.5."""
    roster = D["roster"]; K = D["K"]
    rng = random.Random(seed)
    edges = []; cell_qs = {}
    for name, rs in sorted(cells, key=lambda t: t[0]):
        source = rs[0][1]
        qs = sorted({r[2] for r in rs}); cell_qs[name] = qs
        byq = defaultdict(list)
        for r in rs: byq[r[2]].append(r)
        draws = []
        for _ in range(B_):
            pick = [qs[rng.randrange(len(qs))] for _ in qs]
            sub = [r for q in pick for r in byq[q]]
            draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                        for _, _, _, a, b, w, _ in sub], roster))
        la = {m: sum(K[q][m] for q in qs) / len(qs) for m in roster}
        ev_qs = eval_qs_for(D, name); pool_qs = pool_qs_for(D, name)
        for i, a in enumerate(roster):
            for b in roster[i + 1:]:
                gap = abs(la[a] - la[b])
                d = np.array([dr[a] - dr[b] for dr in draws])
                p = float((d > 0).mean())
                aE, nE = agree_rate(ev_qs, D["XB"], a, b, source)        # A of record: eval side, reading B
                aEA, _ = agree_rate(ev_qs, D["XA"], a, b, source)        # reading A of the extracted answer
                aJ, nJ = agree_rate(qs, D["XB"], a, b, source)           # judged questions
                aP, nP = agree_rate(pool_qs, D["XB"], a, b, source)      # union pool of record, eval side
                extra = {}
                if source == "IFEVAL":
                    extra["agree_prompt"], _ = agree_rate(ev_qs, D["XC_prompt"], a, b, source)
                edges.append(dict(anchor=name, source=source, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                  right=((p > 0.5) == (la[a] > la[b])), agree=aE, n=nE, agree_A=aEA, agree_judged=aJ, n_judged=nJ,
                                  agree_pool=aP, n_pool=nP, gap=gap, ka=la[a], kb=la[b], q=len(qs), q_eval=len(ev_qs), matches=len(rs), **extra))
    return edges, cell_qs


# ------------------------------------------------------------------------------------------------ stats
EXP_CLAMP = 20.0     # systematic_budget.nll clamps the exponent at 20; sb.cbud does not and overflows on a degenerate fit


def cbud(e, b0, b1):
    """sb.cbud with sb.nll's own exponent clamp, so a fold scored with parameters a likelihood fitted cannot overflow.
    Identical to sb.cbud wherever b0 + b1 A < 20 (asserted in main on the fit of record)."""
    tau = math.exp(min(EXP_CLAMP, b0 + b1 * e["agree"]))
    g = float(norm.cdf(abs(e["m"]) / math.sqrt(e["s"] ** 2 + tau ** 2)))
    return min(sb.craw(e), g)


def fit3(es):
    """sb.fit from three starts (Nelder-Mead can stall on a flat ridge); returns (b0, b1, degenerate).
    degenerate = the exponent reaches sb.nll's clamp on the population's own A range: the likelihood has no interior
    maximum (it keeps improving along the ridge b0 ~ -b1 A*, a step in A) and the printed b1 is where the optimiser
    stopped, not an estimate. The sign of the step survives; the magnitude does not."""
    best = None
    for x0 in ((-3.0, 3.0), (-1.0, 0.0), (-5.0, 8.0)):
        c0, c1 = sb.fit(es, x0=x0)
        v = sb.nll((c0, c1), es)
        if best is None or v < best[0] - 1e-9: best = (v, c0, c1)
    _, b0, b1 = best
    amax = max(e["agree"] for e in es); amin = min(e["agree"] for e in es)
    degenerate = (b0 + b1 * amax >= EXP_CLAMP - 1e-6) or (b0 + b1 * amin >= EXP_CLAMP - 1e-6) or abs(b1) > 100
    return b0, b1, degenerate


def support_str(inside, degen):
    if not inside: return "none on the grid"
    return "[%s .. %s" % (inside[0], "+inf)" if (degen and inside[-1] >= 20) else "%s]" % inside[-1])


def profile_b0(es, b1):
    # wide bounds: a degenerate fit's ridge runs along b0 ~ -b1 * A*, so the profile at b1 = 30 needs b0 ~ -20
    r = minimize_scalar(lambda b0: sb.nll((b0, b1), es), bounds=(-400, 50), method="bounded", options=dict(xatol=1e-6))
    return float(r.fun), float(r.x)


def identification(es, b0, b1):
    """delta-deviance at b1 = 0 (b0 re-optimised) against the MLE, plus the profile support region on a grid."""
    d_mle = 2 * sb.nll((b0, b1), es)
    d0, _ = profile_b0(es, 0.0); d0 *= 2
    grid = [-10, -5, -2, -1, 0, 0.5, 1, 1.72, 2, 3, 3.3133, 4, 5, 6, 7.87, 10, 15, 20, 30]
    raw = {g: 2 * profile_b0(es, g)[0] for g in grid}
    d_ref = min([d_mle] + list(raw.values()))      # a degenerate fit's optimiser stop is not the infimum; use the lowest seen
    prof = {g: raw[g] - d_ref for g in grid}
    inside = [g for g in grid if prof[g] <= 3.84]
    return d0 - d_ref, prof, inside


def cp_upper(k, n, conf=0.95):
    if n == 0: return float("nan")
    if k >= n: return 1.0
    return float(beta.ppf(conf, k + 1, n - k))


def status_word(nominal, observed):
    if nominal < 3:
        return "UNDETERMINED (nominal %.2f < 3)" % nominal
    if nominal < 9:
        k = 0
        while poisson.sf(k - 1, nominal) > 0.05: k += 1
        return "UNDETERMINED (power: 2x undetectable; nominal %.2f in [3, 9); smallest callable %d observed = %.2fx)" % (nominal, k, k / nominal)
    ptail = poisson.sf(observed - 1, nominal) if observed > 0 else 1.0
    return ("NOT DETECTABLY MISCALIBRATED" if ptail > 0.05 else "MISCALIBRATED") + " (nominal %.2f, observed %d, Poisson P(>= obs) = %.3f)" % (nominal, observed, ptail)


def status_both(r):
    """Status of record on the ALL-label wrong count (harder); the established count's word beside where it differs."""
    s_all = status_word(r["nominal"], r["wrong"]); s_est = status_word(r["nominal"], r["west"])
    return s_all if s_all == s_est else "%s [on all wrong %d; on established %d: %s]" % (s_all, r["wrong"], r["west"], s_est)


def calib_row(es, K, cell_qs, b0=None, b1=None, thresh=THRESH):
    """called, wrong all(established), nominal, correct surrendered vs the raw certificate, status."""
    if b0 is None:
        called = [e for e in es if sb.craw(e) >= thresh]
        nominal = sum(1 - sb.craw(e) for e in called)
        nominal_gauss = sum(1 - float(norm.cdf(abs(e["m"]) / e["s"])) for e in called)
    else:
        called = [e for e in es if cbud(e, b0, b1) >= thresh]
        nominal = sum(1 - cbud(e, b0, b1) for e in called)
        nominal_gauss = None
    wrong = [e for e in called if not e["right"]]
    west = sb.established(wrong, K, cell_qs)
    return dict(n=len(es), called=len(called), wrong=len(wrong), west=len(west), nominal=nominal, nominal_gauss=nominal_gauss,
                ratio_all=(len(wrong) / nominal if nominal > 0 else float("nan")),
                ratio_est=(len(west) / nominal if nominal > 0 else float("nan")),
                right_called=sum(1 for e in called if e["right"]),
                wrong_edges=wrong, west_edges=west)


def oof_row(pop, oof, K, cell_qs):
    called = [e for e in pop if oof[id(e)] >= THRESH]
    wrong = [e for e in called if not e["right"]]; west = sb.established(wrong, K, cell_qs)
    nom = sum(1 - oof[id(e)] for e in called)
    return dict(n=len(pop), called=len(called), wrong=len(wrong), west=len(west), nominal=nom, nominal_gauss=None,
                ratio_all=(len(wrong) / nom if nom > 0 else float("nan")), ratio_est=(len(west) / nom if nom > 0 else float("nan")),
                right_called=sum(1 for e in called if e["right"]), wrong_edges=wrong, west_edges=west)


def fmt_row(label, r):
    return "  %-44s %6d %7d %9s %8.3f %7s %7s | rate on called %d/%d = %.2f%% (est %.2f%%), 95%% UB %.2f%% (est %.2f%%)%s" % (
        label, r["n"], r["called"], "%d(%d)" % (r["wrong"], r["west"]), r["nominal"],
        ("%.2fx" % r["ratio_all"]) if r["nominal"] > 0 else "-", ("%.2fx" % r["ratio_est"]) if r["nominal"] > 0 else "-",
        r["wrong"], r["called"], 100.0 * r["wrong"] / max(1, r["called"]), 100.0 * r["west"] / max(1, r["called"]),
        100.0 * cp_upper(r["wrong"], r["called"]), 100.0 * cp_upper(r["west"], r["called"]),
        (" | Gaussian nominal %.3f" % r["nominal_gauss"]) if r.get("nominal_gauss") is not None else "")


HDR = "  %-44s %6s %7s %9s %8s %7s %7s" % ("rule", "edges", "called", "wrong", "nominal", "ratio", "r.est")


# ------------------------------------------------------------------------------------------------ main
def main(refresh):
    t0 = time.time(); L = []
    P = lambda s="": L.append(s)
    pool_of_record = pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    D = load()
    P("CERT-CORPUS  (FRAMEWORK item 8; registered by reference at eaf1dbf; 0 LLM calls, 0 network)")
    P("producing code hash: sha256 %s  (%s)" % (hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest(),
                                               os.path.relpath(os.path.abspath(__file__), ROOT).replace(os.sep, "/")))
    P("[POOL-GUARD] mmlu_pro dataset DB pool of record %s verified by id" % pool_of_record)
    P("[POOL-PIN]   multicorpus DB union pool %s verified by id; this script addresses it BY EXPLICIT ID only, as a sensitivity" % D["active"])
    P("item 7 input: %s written %s (%s); MATH extractor: %s; IFEval vector: %s" % (os.path.relpath(CHECKER_DB, ROOT).replace(os.sep, "/"),
      D["meta"].get("written_at"), D["meta"].get("script"), D["meta"].get("math_checker"), D["meta"].get("ifeval_vector", "").split(" from ")[0]))
    V = D["verdicts"]; roster = D["roster"]; K = D["K"]
    n_pairs = len(roster) * (len(roster) - 1) // 2
    P("GEN-ARENA cache: %d valid verdicts (%d invalid), judge grok-4-1-fast-non-reasoning, verifier reference, no rubric, TIE = 0.5 | roster %d models -> %d pairs per cell | excluded: %s"
      % (len(V), D["n_inv"], len(roster), n_pairs, ", ".join(sorted(EXCLUDE))))
    P("  roster: " + ", ".join(roster))
    ties = sum(1 for r in V if r[5] == "TIE")
    P("  ties in the cache: %d of %d = %.1f%% (the certificate reads the TIE = 0.5 board; a tie-heavy board has small |m|)" % (ties, len(V), 100.0 * ties / len(V)))
    # key cross-check: checker DB vs the key GEN-ARENA's outcome used
    n_cmp = n_dis = 0
    for r in V:
        for m in (r[3], r[4]):
            g1 = D["G_ga"].get(r[2], {}).get(m); g2 = K.get(r[2], {}).get(m)
            if g1 is None or g2 is None: continue
            n_cmp += 1; n_dis += int(g1 != g2)
    P("  key: checker_answers_v1.db checker_correct (MATH: MATH-FIX; IFEval: prompt-level strict) vs generative_arena.correctness(): %d of %d judged (question, model) cells differ; checker_correct vs mathfix_correct: %d rows differ" % (n_dis, n_cmp, D["n_diff"]))
    assert n_dis == 0 and D["n_diff"] == 0, "the checker key and GEN-ARENA's key disagree"

    # cells
    by_src = defaultdict(list); by_dom = defaultdict(list)
    for r in V:
        by_src[r[1]].append(r); by_dom[cell_of(D, r[2])].append(r)
    rows = [(s, by_src[s]) for s in ("MATH", "IFEVAL")]
    dom_cells = [(d, rs) for d, rs in by_dom.items() if d.startswith("MATH/")]
    P()
    P("CELLS and KEY DENOMINATOR (McNemar over the cell's judged questions; A over the cell's eval-side questions of GEN-ARENA's own split):")
    sched_q = defaultdict(set)
    for _, s, q, a, b in D["sched"]: sched_q[s].add(q)
    for name, rs in rows + sorted(dom_cells):
        qs = {r[2] for r in rs}
        in_pool = len(qs & D["pool"]); ev = eval_qs_for(D, name)
        n_sched = len(sched_q[name]) if name in ("MATH", "IFEVAL") else len({q for q in sched_q["MATH"] if cell_of(D, q) == name})
        P("  %-30s matches %5d | judged q %4d | scheduled q %4d | eval side of GEN-ARENA's Random(42) split %4d (judged not on it: %d) | judged in union pool %s %4d"
          % (name, len(rs), len(qs), n_sched, len(ev), len(qs - set(ev)), UNION_POOL, in_pool))
    P("  floors: build() 200 matches -> MATH domain cells admitted: %s; JUDGE-TRANSFER 100 -> %s"
      % (", ".join(sorted(d for d, rs in dom_cells if len(rs) >= FLOOR_BUILD)), ", ".join(sorted(d for d, rs in dom_cells if len(rs) >= FLOOR_JT))))

    # D_c per cell on THIS roster: is the cell a checker cell?
    P()
    P("D_c PER CELL ON THE GEN-ARENA ROSTER (%d pairs; eval-side questions of the board's split; item 7 reading B = checker of record + NON_TERMINATED -> blank; question bootstrap B = %d, 95%% interval):" % (n_pairs, B_DC))
    P("  %-30s %6s %8s %18s %8s  %s" % ("cell", "q_eval", "D_c (B)", "95% CI", "D_c (A)", "class by Stage 1 (bar %.2f)" % DC_BAR))
    checker_cell = {}
    for name, rs in rows + sorted(dom_cells):
        ev = eval_qs_for(D, name)
        dB, lo, hi = dc_cell(ev, D["XB"], roster); dA, _, _ = dc_cell(ev, D["XA"], roster, B_=1)
        checker_cell[name] = dB >= DC_BAR
        P("  %-30s %6d %8.4f [%6.4f, %6.4f] %8.4f  %s%s" % (name, len(ev), dB, lo, hi, dA,
          "checker cell (edge pass admissible)" if dB >= DC_BAR else "PREDICTIVE-ONLY (D_c < %.2f)" % DC_BAR,
          "" if lo >= DC_BAR or hi < DC_BAR else "; interval crosses the bar"))
    P("  item 7's verdict of record on the 18-model roster: MATH row 0.8268 [0.8184, 0.8350] -> PREDICTIVE-ONLY there; the shortfall is the two R1 distills")
    P("  (NON_TERMINATED on 284/398 and 316/398 eval-side questions), neither of which GEN-ARENA judged. This board's own D_c governs the product read here.")
    non_checker = sorted(n for n, ok in checker_cell.items() if not ok)
    P("  cells excluded from the product read as PREDICTIVE-ONLY: %s" % (", ".join(non_checker) if non_checker else "none"))

    # edges (cached)
    if os.path.exists(CACHE) and not refresh:
        E = json.load(open(CACHE, encoding="utf-8"))
        P("  edge tables read from cache %s" % CACHE)
    else:
        os.makedirs(SCRATCH, exist_ok=True)
        e_rows, cq_rows = build_edges(D, rows, B, 42)
        e_dom, cq_dom = build_edges(D, dom_cells, B, 42)
        e_tail, _ = build_edges(D, rows, B_TAIL, 2026)
        E = dict(rows=e_rows, cq_rows=cq_rows, dom=e_dom, cq_dom=cq_dom, tail=e_tail)
        json.dump(E, open(CACHE, "w", encoding="utf-8"))
        P("  edge tables built and cached at %s" % CACHE)
    cell_qs = {}; cell_qs.update(E["cq_rows"]); cell_qs.update(E["cq_dom"])
    # gap == 0 edges carry no label; the unfiltered set is gap > 0 (SYSTEMATIC-BUDGET correction (b))
    rows_all = [e for e in E["rows"] if e["gap"] > 0]
    rows_zero = [e for e in E["rows"] if e["gap"] == 0]
    dom_all = {floor: [e for e in E["dom"] if e["gap"] > 0 and e["matches"] >= floor] for floor in (FLOOR_BUILD, FLOOR_JT)}
    # readings A and B of item 7 coincide on this roster
    n_ab = sum(1 for e in E["rows"] + E["dom"] if abs((e["agree"] or 0) - (e["agree_A"] or 0)) > 1e-12)
    P("  A under item 7's reading A vs reading B on this roster: %d of %d edges differ (no R1 distill on the roster)" % (n_ab, len(E["rows"]) + len(E["dom"])))
    assert n_ab == 0
    dJ = [abs(e["agree"] - e["agree_judged"]) for e in E["rows"]]
    P("  A of record (eval side, MATH 397 / IFEVAL 162 q) vs A over the judged questions (394 / 162): max |dA| %.4f, median %.4f over the %d row edges" % (max(dJ), float(np.median(dJ)), len(dJ)))

    # ---------------------------------------------------------------- the edge table of record
    P()
    P("=" * 118)
    P("EDGE TABLE OF RECORD: the two registered GEN-ARENA boards, %d pairs each, B = %d question bootstrap (Random(42), build() order)" % (n_pairs, B))
    P("=" * 118)
    P("  %-7s %-28s %-28s %6s %6s %6s %6s %6s %6s %5s %6s %6s %-14s %s" % ("cell", "a", "b", "m", "s", "c_raw", "A", "A.jdg", "A.pool", "n_A", "keya", "keyb", "McNemar b:c p", "label"))
    for e in sorted(E["rows"], key=lambda e: (e["anchor"], -sb.craw(e))):
        pv, b_, c_ = sb.mcnemar_edge(e, K, cell_qs)
        lab = ("unlabeled (gap 0)" if e["gap"] == 0 else ("right" if e["right"] else "WRONG")) + (" est" if pv < 0.05 else " indet")
        P("  %-7s %-28s %-28s %+6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %5d %6.3f %6.3f %3d:%-3d %.4f %s"
          % (e["anchor"], e["a"][:28], e["b"][:28], e["m"], e["s"], sb.craw(e), e["agree"], e["agree_judged"],
             e["agree_pool"] if e["agree_pool"] is not None else float("nan"), e["n"], e["ka"], e["kb"], b_, c_, pv, lab))
    P("  unlabeled (gap = 0) edges dropped from every count: %d" % len(rows_zero))
    for src in ("MATH", "IFEVAL"):
        es = [e for e in rows_all if e["anchor"] == src]
        ss = sorted(e["s"] for e in es); aa = sorted(e["agree"] for e in es)
        est = sb.established(es, K, cell_qs)
        P("  %-7s %d labelled edges: %d wrong (%d established) | established %d of %d | s median %.3f (p10 %.3f, p90 %.3f) | A median %.3f (min %.3f, max %.3f)"
          % (src, len(es), sum(1 for e in es if not e["right"]), sum(1 for e in est if not e["right"]), len(est), len(es),
             ss[len(ss) // 2], ss[len(ss) // 10], ss[9 * len(ss) // 10], aa[len(aa) // 2], aa[0], aa[-1]))
    P("  x12 reference scale: the shipped fit's population has s in 0.20-0.30 (per-anchor median 0.246); tau(A) = exp(b0 + b1 A) is read against it")

    # ---------------------------------------------------------------- (a) raw miscalibration
    P()
    P("=" * 118)
    P("(a) RAW MISCALIBRATION READ: the raw bootstrap certificate at %.3f (TIER-HONEST's reading), wrong as all(established); nominal = sum(1 - c_raw)" % THRESH)
    P("=" * 118)
    P(HDR)
    raw_rows = calib_row(rows_all, K, cell_qs)
    P(fmt_row("registered rows (MATH + IFEVAL), unfiltered", raw_rows))
    for src in ("MATH", "IFEVAL"):
        P(fmt_row("  %s row" % src, calib_row([e for e in rows_all if e["anchor"] == src], K, cell_qs)))
    P(fmt_row("registered rows, gap >= %.2f (beside, not used)" % GAP, calib_row([e for e in rows_all if e["gap"] >= GAP], K, cell_qs)))
    for floor in (FLOOR_BUILD, FLOOR_JT):
        P(fmt_row("IFEVAL row + MATH domain cells, floor %d" % floor, calib_row([e for e in rows_all if e["anchor"] == "IFEVAL"] + dom_all[floor], K, cell_qs)))
        P(fmt_row("  MATH domain cells alone, floor %d" % floor, calib_row(dom_all[floor], K, cell_qs)))
    tail_all = [e for e in E["tail"] if e["gap"] > 0]
    raw_tail = calib_row(tail_all, K, cell_qs)
    P(fmt_row("registered rows at B = %d (c_raw tail sensitivity)" % B_TAIL, raw_tail))
    P("  status of the RAW certificate on the registered rows by the power rule: %s" % status_both(raw_rows))
    if raw_rows["wrong_edges"]:
        P("  raw wrong calls on the registered rows:")
        for e in raw_rows["wrong_edges"]:
            pv, b_, c_ = sb.mcnemar_edge(e, K, cell_qs)
            P("    %-7s %s vs %s: c_raw %.4f, m %+.3f, s %.3f, A %.3f, key %.3f vs %.3f (gap %.3f), McNemar %d:%d p = %.4f -> %s"
              % (e["anchor"], e["a"], e["b"], sb.craw(e), e["m"], e["s"], e["agree"], e["ka"], e["kb"], e["gap"], b_, c_, pv, "ESTABLISHED" if pv < 0.05 else "indeterminate"))
    P("  x12 for scale (Mistral, MMLU-Pro, 920 unfiltered edges): raw 748 called / 11 wrong = 1.47%; TIER-HONEST 739 / 8 vs 0.83 nominal")
    P("  the two edges on which GEN-ARENA's registered BRIDGE broke (judged argmax vs key argmax), as the certificate reads them:")
    for src, a_, b_ in (("MATH", "Qwen2.5-32B-Instruct", "Qwen2.5-72B-Instruct"), ("IFEVAL", "Llama-3.3-70B-Instruct", "Qwen2.5-72B-Instruct")):
        for e in rows_all:
            if e["anchor"] == src and {e["a"], e["b"]} == {a_, b_}:
                pv, bb, cc = sb.mcnemar_edge(e, K, cell_qs)
                P("    %-7s %s vs %s: c_raw %.3f (%s at 0.975), key direction %s, McNemar %d:%d p = %.4f (%s) -> class %s"
                  % (src, a_, b_, sb.craw(e), "CALLED" if sb.craw(e) >= THRESH else "not called", "right" if e["right"] else "WRONG", bb, cc, pv,
                     "established" if pv < 0.05 else "indeterminate",
                     ("KEY-CONTRADICTED" if (sb.craw(e) >= THRESH and not e["right"] and pv < 0.05) else ("ORDERED" if (sb.craw(e) >= THRESH and pv < 0.05) else "BANDED (no ORDERED edge)"))))

    # ---------------------------------------------------------------- (b) the widener fit
    P()
    P("=" * 118)
    P("(b) WIDENER FIT tau(A) = exp(b0 + b1 A) on the GEN-ARENA edges (systematic_budget.fit / nll; sign and identification)")
    P("=" * 118)
    P("  %-52s %5s %5s %9s %9s %10s %8s %s" % ("population", "edges", "wrong", "b0", "b1", "dDev(b1=0)", "ident.", "profile support b1 (dDev <= 3.84) on the grid"))
    fits = {}
    pops = [("registered rows, all labels [FIT OF RECORD, all]", rows_all),
            ("registered rows, ESTABLISHED labels [FIT OF RECORD, est]", sb.established(rows_all, K, cell_qs)),
            ("  MATH row, all labels", [e for e in rows_all if e["anchor"] == "MATH"]),
            ("  MATH row, established", sb.established([e for e in rows_all if e["anchor"] == "MATH"], K, cell_qs)),
            ("  IFEVAL row, all labels", [e for e in rows_all if e["anchor"] == "IFEVAL"]),
            ("  IFEVAL row, established", sb.established([e for e in rows_all if e["anchor"] == "IFEVAL"], K, cell_qs))]
    for floor in (FLOOR_BUILD, FLOOR_JT):
        pop = [e for e in rows_all if e["anchor"] == "IFEVAL"] + dom_all[floor]
        pops.append(("IFEVAL row + MATH domains (floor %d), all labels" % floor, pop))
        pops.append(("IFEVAL row + MATH domains (floor %d), established" % floor, sb.established(pop, K, cell_qs)))
        pops.append(("  MATH domains alone (floor %d), all labels" % floor, dom_all[floor]))
        pops.append(("  MATH domains alone (floor %d), established" % floor, sb.established(dom_all[floor], K, cell_qs)))
    for label, es in pops:
        nw = sum(1 for e in es if not e["right"])
        if len(es) < 5 or nw == 0:
            P("  %-52s %5d %5d %9s %9s %10s %8s %s" % (label, len(es), nw, "-", "-", "-", "-", "no wrong-direction edge: the likelihood has no interior maximum (tau -> 0), nothing to fit"))
            fits[label] = None; continue
        b0, b1, degen = fit3(es)
        dd, prof, inside = identification(es, b0, b1)
        fits[label] = (b0, b1, dd, inside, degen)
        P("  %-52s %5d %5d %+9.4f %+9.4f %10.2f %8s %s" % (label, len(es), nw, b0, b1, dd, "YES" if dd >= 3.84 else "no",
                                                             support_str(inside, degen) + ("; grid dDev: " + " ".join("%g:%.1f" % (g, prof[g]) for g in (0, 1.72, 3.3133, 7.87) if g in prof))
                                                             + ("  ** DEGENERATE: no interior maximum (a step in A at %.3f); b1 is where the optimiser stopped **" % (-b0 / b1) if degen else "")))
    P("  x12 reference: b1 = +3.3133 (891) / +3.1980 (920), CI [1.72, 7.87]; grok MMLU-Pro (JUDGE-TRANSFER): +3.58 all labels, degenerate (tau -> 0) on established labels")
    P("  READ: b1 > 0 means the widener GROWS with answer agreement (SYSTEMATIC-SIGNAL's direction); b1 < 0 means the opposite; a flat")
    P("        profile (no bound on either side) means the data do not locate b1 and the sign is not a finding.")

    # ---------------------------------------------------------------- (c) calibration statement per board under the fit
    P()
    P("=" * 118)
    P("(c) CALIBRATION STATEMENT under the fitted widener at %.3f; status word by the power rule" % THRESH)
    P("=" * 118)
    P(HDR)
    rec = fits["registered rows, all labels [FIT OF RECORD, all]"]
    rec_est = fits["registered rows, ESTABLISHED labels [FIT OF RECORD, est]"]
    verdict_rows = {}; r_in = None
    if rec:
        r_in = calib_row(rows_all, K, cell_qs, rec[0], rec[1]); verdict_rows["in-sample, all-label fit"] = r_in
        P(fmt_row("registered rows, in sample (all-label fit)", r_in))
        P("    -> " + status_both(r_in))
        P("    utility: %d of %d unfiltered edges called = %.1f%% (bar 60%%); raw calls retained %d of %d; correct surrendered %d for %d wrong (%d est) removed"
          % (r_in["called"], r_in["n"], 100.0 * r_in["called"] / r_in["n"], r_in["called"], raw_rows["called"], raw_rows["right_called"] - r_in["right_called"], raw_rows["wrong"] - r_in["wrong"], raw_rows["west"] - r_in["west"]))
        created = sum(1 for e in rows_all if cbud(e, rec[0], rec[1]) > sb.craw(e) + 1e-9)
        assert all(abs(cbud(e, rec[0], rec[1]) - sb.cbud(e, rec[0], rec[1])) < 1e-12 for e in rows_all), "local cbud must equal sb.cbud off the clamp"
        P("    monotonicity: edges the widener makes MORE confident: %d (must be 0)" % created)
        P("    tau at A = 0.30 / 0.45 / 0.60 / 0.80 / 0.90: %s  (vs s median MATH %.3f, IFEVAL %.3f)"
          % (" / ".join("%.3f" % math.exp(rec[0] + rec[1] * a) for a in (0.30, 0.45, 0.60, 0.80, 0.90)),
             float(np.median([e["s"] for e in rows_all if e["anchor"] == "MATH"])), float(np.median([e["s"] for e in rows_all if e["anchor"] == "IFEVAL"]))))
    if rec_est:
        r_ie = calib_row(rows_all, K, cell_qs, rec_est[0], rec_est[1]); verdict_rows["in-sample, established fit"] = r_ie
        P(fmt_row("registered rows, in sample (established-label fit%s)" % (", DEGENERATE step" if rec_est[4] else ""), r_ie))
        P("    -> " + status_both(r_ie))
        P("    utility: %d of %d = %.1f%%" % (r_ie["called"], r_ie["n"], 100.0 * r_ie["called"] / r_ie["n"]))
    # leave-one-cell-out on the registered rows (two folds; each fold fits on the other row's edges)
    oof = {}
    fold_note = []
    for src in ("MATH", "IFEVAL"):
        tr = [e for e in rows_all if e["anchor"] != src]; te = [e for e in rows_all if e["anchor"] == src]
        if sum(1 for e in tr if not e["right"]) == 0:
            fold_note.append("%s fold: training cell has 0 wrong edges, tau -> 0, the fold degenerates to the raw certificate" % src)
            for e in te: oof[id(e)] = sb.craw(e)
            continue
        f0, f1, dg = fit3(tr)
        fold_note.append("%s fold: fitted on %s (%d edges): b0 %+.3f, b1 %+.3f%s" % (src, tr[0]["anchor"], len(tr), f0, f1, " DEGENERATE (no interior maximum, a step in A; scored with sb.nll's clamp)" if dg else ""))
        for e in te: oof[id(e)] = cbud(e, f0, f1)
    r_lo = oof_row(rows_all, oof, K, cell_qs)
    verdict_rows["leave-one-cell-out"] = r_lo
    P(fmt_row("registered rows, LEAVE-ONE-CELL-OUT (2 folds)", r_lo))
    for n_ in fold_note: P("    " + n_)
    P("    -> " + status_both(r_lo))
    # domain-level fits, leave-one-cell-out
    for floor in (FLOOR_BUILD, FLOOR_JT):
        pop = [e for e in rows_all if e["anchor"] == "IFEVAL"] + dom_all[floor]
        lab = "IFEVAL row + MATH domains (floor %d), all labels" % floor
        f = fits.get(lab)
        if f:
            r_d = calib_row(pop, K, cell_qs, f[0], f[1])
            P(fmt_row("IFEVAL + MATH domains floor %d, in sample" % floor, r_d))
            P("    -> %s | utility %.1f%%" % (status_both(r_d), 100.0 * r_d["called"] / r_d["n"]))
        cells_ = sorted({e["anchor"] for e in pop}); oofd = {}
        for c_ in cells_:
            tr = [e for e in pop if e["anchor"] != c_]; te = [e for e in pop if e["anchor"] == c_]
            if sum(1 for e in tr if not e["right"]) == 0:
                for e in te: oofd[id(e)] = sb.craw(e)
                continue
            f0, f1, _ = fit3(tr)
            for e in te: oofd[id(e)] = cbud(e, f0, f1)
        r_ld = oof_row(pop, oofd, K, cell_qs)
        P(fmt_row("IFEVAL + MATH domains floor %d, LEAVE-ONE-CELL-OUT (%d folds)" % (floor, len(cells_)), r_ld))
        P("    -> " + status_both(r_ld))
        verdict_rows["domains floor %d LOCO" % floor] = r_ld

    # ---------------------------------------------------------------- (d) x12 parameters cold, labelled diagnostic
    P()
    P("=" * 118)
    P("(d) DIAGNOSTIC ONLY: the shipped x12 (Mistral / MMLU-Pro) parameters applied cold. Stage 6 stores parameters per (board id,")
    P("    judge_model) and REFUSES them elsewhere; these rows are NOT a certificate and adjudicate nothing.")
    P("=" * 118)
    P(HDR)
    for tag, (b0, b1) in (("x12 891 pair (%.4f, %.4f)" % X12_891, X12_891), ("x12 920 pair (%.4f, %.4f)" % X12_920, X12_920)):
        r_c = calib_row(rows_all, K, cell_qs, b0, b1)
        P(fmt_row("registered rows, cold " + tag, r_c))
        P("    utility %.1f%%; %d correct surrendered for %d wrong (%d est) removed | tau at the rows' A median: MATH %.3f, IFEVAL %.3f vs s median MATH %.3f, IFEVAL %.3f"
          % (100.0 * r_c["called"] / r_c["n"], raw_rows["right_called"] - r_c["right_called"], raw_rows["wrong"] - r_c["wrong"], raw_rows["west"] - r_c["west"],
             math.exp(b0 + b1 * float(np.median([e["agree"] for e in rows_all if e["anchor"] == "MATH"]))),
             math.exp(b0 + b1 * float(np.median([e["agree"] for e in rows_all if e["anchor"] == "IFEVAL"]))),
             float(np.median([e["s"] for e in rows_all if e["anchor"] == "MATH"])), float(np.median([e["s"] for e in rows_all if e["anchor"] == "IFEVAL"]))))
    # agreement gate, for the comparison SYSTEMATIC-BUDGET (5) always prints
    rc = [e for e in rows_all if sb.craw(e) >= THRESH]
    P("  one-line agreement gate on the raw calls (SYSTEMATIC-BUDGET (5)'s comparison): ")
    for t in (0.60, 0.70, 0.80, 0.85, 0.90):
        g = [e for e in rc if e["agree"] < t]; gw = [e for e in g if not e["right"]]
        P("    gate A < %.2f: %d called, %d wrong (%d est), %d correct surrendered" % (t, len(g), len(gw), len(sb.established(gw, K, cell_qs)), raw_rows["right_called"] - sum(1 for e in g if e["right"])))

    # ---------------------------------------------------------------- (e) sensitivities
    P()
    P("=" * 118)
    P("(e) SENSITIVITIES")
    P("=" * 118)
    for key, label, nq in (("agree_judged", "A over the cell's JUDGED questions (MATH 394 q, IFEVAL 162 q)", ""),
                           ("agree_pool", "A over the union pool %s eval side (MATH 398 q, IFEVAL 162 q)" % UNION_POOL, "")):
        swapped = []
        for e in rows_all:
            f = dict(e); f["agree"] = e[key] if e[key] is not None else e["agree"]; swapped.append(f)
        dA = [abs(e["agree"] - f["agree"]) for e, f in zip(rows_all, swapped)]
        P("  %s instead of the eval side of record: max |dA| %.4f, median %.4f" % (label, max(dA), float(np.median(dA))))
        if rec:
            r_s = calib_row(swapped, K, cell_qs, rec[0], rec[1])
            P("    " + fmt_row("registered rows, record fit, swapped A", r_s).strip())
            if sum(1 for e in swapped if not e["right"]) > 0:
                s0, s1, sdg = fit3(swapped); dd, _, inside = identification(swapped, s0, s1)
                r_sf = calib_row(swapped, K, cell_qs, s0, s1)
                P("    refit with swapped A: b0 %+.4f, b1 %+.4f, dDev(b1=0) %.2f, support %s%s | in sample called %d / %d, wrong %d(%d), nominal %.3f, utility %.1f%%"
                  % (s0, s1, dd, support_str(inside, sdg), " DEGENERATE" if sdg else "", r_sf["called"], r_sf["n"], r_sf["wrong"], r_sf["west"], r_sf["nominal"], 100.0 * r_sf["called"] / r_sf["n"]))
    # IFEval prompt-level agreement instead of vector agreement
    ife = [e for e in rows_all if e["anchor"] == "IFEVAL"]
    P("  IFEVAL A as prompt-level agreement (both pass or both fail) instead of identical vectors: A median %.3f vs %.3f (vector)"
      % (float(np.median([e["agree_prompt"] for e in ife])), float(np.median([e["agree"] for e in ife]))))
    # B = 2000 tail: c_raw at 0.975 on the registered rows
    ch = 0
    tail_by = {(e["anchor"], e["a"], e["b"]): e for e in tail_all}
    for e in rows_all:
        t = tail_by.get((e["anchor"], e["a"], e["b"]))
        if t and ((sb.craw(e) >= THRESH) != (sb.craw(t) >= THRESH)): ch += 1
    P("  raw calls that change between B = %d and B = %d on the registered rows: %d of %d" % (B, B_TAIL, ch, len(rows_all)))
    if rec:
        r_t = calib_row(tail_all, K, cell_qs, rec[0], rec[1])
        P("    " + fmt_row("registered rows at B = %d, record fit" % B_TAIL, r_t).strip())
    # what nominal 3 would take
    if rec and r_in["nominal"] > 0:
        P("  support arithmetic: nominal %.3f on %d called edges -> nominal 3 needs ~%.0fx the edge count at this per-edge nominal (~%d called edges); nominal 9 ~%d"
          % (r_in["nominal"], r_in["called"], 3 / r_in["nominal"], round(3 / r_in["nominal"] * r_in["called"]), round(9 / r_in["nominal"] * r_in["called"])))

    # ---------------------------------------------------------------- CRITERIA
    P()
    P("=" * 118)
    P("CRITERIA (item 8 wording). Key denominator: the cell's judged questions in the GEN-ARENA cache (MATH 394, IFEVAL 162)")
    P("=" * 118)
    P("(1) 'calibration status by the power rule' on the fit of record (registered rows, unfiltered edges, wrong as all(established); status on the all-label count):")
    for k_, r_ in verdict_rows.items():
        P("      %-34s called %4d / %d, wrong %d(%d), nominal %.3f -> %s" % (k_, r_["called"], r_["n"], r_["wrong"], r_["west"], r_["nominal"], status_both(r_)))
    st_in = status_both(r_in) if rec else "no fit (0 wrong edges)"
    P("      STATUS OF RECORD (in sample, all-label fit): %s" % st_in)
    P("      raw certificate on the same rows: called %d / %d, wrong %d(%d), nominal %.3f (Gaussian %.3f) -> %s"
      % (raw_rows["called"], raw_rows["n"], raw_rows["wrong"], raw_rows["west"], raw_rows["nominal"], raw_rows["nominal_gauss"], status_both(raw_rows)))
    P("      raw certificate at B = %d: called %d / %d, wrong %d(%d), nominal %.3f (Gaussian %.3f) -> %s"
      % (B_TAIL, raw_tail["called"], raw_tail["n"], raw_tail["wrong"], raw_tail["west"], raw_tail["nominal"], raw_tail["nominal_gauss"], status_both(raw_tail)))
    noms = [r_["nominal"] for r_ in verdict_rows.values()] + [raw_rows["nominal"], raw_rows["nominal_gauss"], raw_tail["nominal"], raw_tail["nominal_gauss"]]
    pred_held = all(n_ < 3 for n_ in noms)
    P("(P) prediction 'UNDETERMINED (nominal < 3)': %s (every nominal above is %s 3; the largest is %.3f)"
      % ("HELD" if pred_held else "NOT HELD", "below" if pred_held else "not all below", max(noms)))
    P("(product) the widener's SIGN on checker cells (cells with D_c >= %.2f on this roster: %s):" % (DC_BAR, "all read cells" if not non_checker else "excluding " + ", ".join(non_checker)))
    for label in ("registered rows, all labels [FIT OF RECORD, all]", "registered rows, ESTABLISHED labels [FIT OF RECORD, est]",
                  "IFEVAL row + MATH domains (floor %d), all labels" % FLOOR_BUILD, "IFEVAL row + MATH domains (floor %d), established" % FLOOR_BUILD,
                  "IFEVAL row + MATH domains (floor %d), all labels" % FLOOR_JT, "IFEVAL row + MATH domains (floor %d), established" % FLOOR_JT):
        f = fits.get(label)
        if f is None:
            P("      %-58s no fit (0 wrong-direction edges; tau -> 0 is the MLE)" % label)
        else:
            b0, b1, dd, inside, degen = f
            P("      %-58s b1 %+8.4f (%s), dDev(b1 = 0) %.2f -> %s; support %s%s"
              % (label, b1, "positive" if b1 > 0 else "NEGATIVE", dd, "identified" if dd >= 3.84 else "NOT identified",
                 support_str(inside, degen),
                 ("; DEGENERATE (a step in A at %.3f): the sign is a direction, the magnitude is not an estimate" % (-b0 / b1)) if degen else ""))
    P("(product) UTILITY on checker cells (share of unfiltered edges called at 0.975; bar 60% from SYSTEMATIC-BUDGET (2)):")
    P("      raw certificate: %.1f%%" % (100.0 * raw_rows["called"] / raw_rows["n"]))
    for k_, r_ in verdict_rows.items():
        P("      %-34s %.1f%% -> %s" % (k_, 100.0 * r_["called"] / r_["n"], "above the bar" if r_["called"] / r_["n"] >= 0.60 else "BELOW the bar"))
    P("      Stage 6 gate: the widener ships on a board only from a fit on that judge's own calibration board whose established-label profile rejects b1 = 0;")
    P("      here it does not, so the certificate on the GEN-ARENA boards runs in FALLBACK (raw certificate + reservation list; edges BANDED-JUDGED, never ORDERED-JUDGED).")
    P("McNemar: every wrong count above is all(established), established = exact two-sided McNemar p < 0.05 on the cell's judged questions (systematic_budget.mcnemar_edge).")
    P("elapsed %.0f s" % (time.time() - t0))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--refresh", action="store_true")
    main(ap.parse_args().refresh)
