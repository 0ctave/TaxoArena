"""AGREE-ORDER (registered 2026-09-19 before any code or call, commit 5205c1d, docs/judge_v2_program.md L8065-L8222;
zero calls) - is the reproducible non-key order carried by the same-answer (AGREE) matches the filter removes a LENGTH
order, a POSITION order, or a contestant-identity order? with the deviation-residue leg registered expecting UNDETERMINED.

  python tools/analysis/agree_order.py --selftest   # synthetic boards (pure-length, pure-identity, null, planted position);
                                                    # nothing of record is opened
  python tools/analysis/agree_order.py --dry-run    # pool id, the pins, the six filter counts (the C0 count gate), the
                                                    # matched-set size per anchor, the 8 cells' match counts; no R, no beta
  python tools/analysis/agree_order.py --run        # write-once outcome + agree_order_cells.csv (8 rows) + agree_order_models.csv
                                                    # (20 rows) from the complete caches; every criterion / prediction /
                                                    # falsifier scored as registered

THE REGISTRATION (the last bracket in the programme file wins over this copy), condensed:
  Data objects: the merged board x12 9,142 + x20 12,394 = 21,536 verdicts (never x20 alone), 20 models, Meta-Llama-3-70B-
  Instruct absent, 2,811 judged questions, 14 bareq512_s42 anchors; AGREE = the two contestants' eval_results.pred equal under
  the shipped MatchFilter.kt rule (trim, case-insensitive, whole string), both present: x12 3,076 + x20 5,846 = 8,922; the
  790 + 1,382 UNDETERMINED-prediction matches are NOT AGREE; DISAGREE 5,276 + 5,166 = 10,442 (conv B's kept set). Length =
  len(eval_results.model_output) in characters (H3's variable). Verdict = the dual-order verdict of record; decisive = not TIE.
  GATE C0: the AGREE-only board R reproduces the reviewer's 0.648 to 2 dp (40 halvings Random(7), model-demeaned) and the six
  counts exactly.
  (L1) H3's logistic on AGREE decisive matches: verdict-for-A ~ beta_len x (len_A - len_B)/1,000 + both-right indicator,
       question-clustered SE, on x12 / x20 / merged; both-right and both-wrong subsets beside; DISAGREE decisive beta beside.
  (L2) Spearman over the 20 models of theta_AGREE with the model's mean output length on the judged questions.
  (L3) the length-MATCHED (|len_A - len_B| <= 300) AGREE-only split-half R, model-demeaned (interaction-only beside), with the
       matched count per anchor and a random same-size subsample of AGREE (5 seeds) as the support comparator;
       UNDETERMINED-by-support if any anchor's matched set is below 120 distinct questions (printed; R still read).
  (P)  on AGREE vs DISAGREE matches: the share whose two single-order verdicts both favour the FIRST position, the share
       decided consistently for one contestant, the tie rate; question-clustered CI on the AGREE - DISAGREE difference.
  (I)  Spearman(theta_AGREE, unfiltered merged theta) and (theta_AGREE, key accuracy); the AGREE top-4 as a SET against the
       key's top cluster; Spearman(theta_matched, mean length).
  (D)  8 wrong-sign PROFILE-DEVIATION-CERT cells: among m's in-anchor decisive wins, the share where m's answer is the longer,
       against the anchor's both-right decisive longer-wins share; question-clustered CI; UNDETERMINED below 120 distinct
       questions behind the wins or with a CI including 0; the 3 established cells flagged; the other 14 certified cells beside.
  Beside, descriptive: beta_len on AGREE by anchor (14 rows) and by TOPIC-DIFFICULTY tercile.
  Criteria: C0 gate; C1 beta_len(AGREE decisive, merged) >= +2.5 / 1k with the clustered CI excluding 0 AND matched R < 0.50;
  C2 |AGREE - DISAGREE first-position-consistent share| < 2pp or CI including 0; C3 reported (largest of the three
  correlations named). Predictions P1-P8 (registration L8151-8161). Falsifier F1: matched AGREE-only R >= 0.60 at the point.
  Verdict rule (L8145-8149): C1 HELD -> verbosity sentence; C1 FAILED with F1 fired -> "unexplained judge order" sentence;
  half-held -> UNDETERMINED with both numbers.

READINGS CHOSEN where the registration is silent or not implementable literally (each stated here before the run):
  * Lengths and the key are read from eval_results by (question_id, model_name); the caches' qid IS the eval question_id
    (the same join PROFILE-R-FILTERED and H3 use), so no mmlu_pro join is needed and question_text is never touched.
  * H3's logistic is bias_audit._logit3 (three coefficients: intercept, dlen/1k, x2). On the merged / per-cache AGREE
    decisive fit x2 = the both-right indicator (0/1). On the both-right and both-wrong SUBSETS the indicator is constant, so
    x2 is set to 0 there (a two-parameter fit inside the same routine; the third coefficient is then not identified
    (_logit3's 1e-9 ridge fills every Hessian entry) and is neither printed nor used; the selftest checks beta_len of
    that call against an independent two-parameter Newton fit to 1e-6). On the DISAGREE decisive comparator x2 = gtDiff
    (H3's own specification).
    The question-clustered SE is the sandwich H^-1 (sum_q g_q g_q^T) H^-1 at the fitted coefficients (this script's
    cluster_se); the model-based SE from _logit3 is printed beside.
  * theta_AGREE "pooled over anchors by the merged fit's rule" is read as the merged board's own fit rule: ONE BT fit
    (rj.mm_fit via judge_free_tests.board_from, prior 0.5, TIE = 0.5) on all AGREE matches pooled over anchors; the mean of
    the 14 per-anchor BT thetas is printed beside as the alternative pooling. P2 / C3 / P7 are read on the pooled fit; the
    alternative pooling's Spearman is printed and any disagreement on a label is flagged.
  * Mean output length per model = mean len(model_output) over the 2,811 judged questions (all 20 models have a row on
    every judged question is asserted; otherwise the per-model denominator is printed). Key accuracy per model = mean
    is_correct over the same questions. The key's top cluster = rj.TOP_CLUSTER (the four named models); the key top-4 by
    accuracy on the judged questions is printed beside; both as sorted sets.
  * (P) "position-consistent" is read literally as both single-order verdicts favouring the FIRST-presented answer
    (vote1 == 'Model A' and vote2_raw == 'Model A'); the both-SECOND share and the union are printed beside; C2 / P6 are
    scored on the literal (first-position) share, and the union's label is printed beside. The CI on the difference is a
    question-clustered bootstrap (questions resampled with replacement over the union of AGREE and DISAGREE questions,
    B = 1,000, Random(2026), percentile 2.5 / 97.5), because a question contributes to both groups.
  * (D) "longer" = strictly longer (equal lengths counted as not longer; their count printed). The baseline is the anchor's
    both-right decisive matches (all pairs, m's included) and the share where the WINNER is the longer answer. The CI on the
    difference is a question-clustered bootstrap within the anchor (B = 1,000, Random(2026)).
  * Difficulty terciles (descriptive leg only) follow topic_difficulty.py: difficulty(q) = fraction of the keyed roster
    (every eval_results model except Meta-Llama-3-70B-Instruct) correct on q; rank terciles WITHIN each anchor over its
    judged questions, ties broken by qid, easy = the top third.
  * The random same-size comparator (L3) draws, per anchor, the matched count from that anchor's AGREE matches (seeds
    42..46), as prf_control.py's support reading did; the reviewer's random-from-the-whole-board band (0.46-0.50 at AGREE's
    size, seeds 42..44) is recomputed beside so C1's "random-match band" has its number in the file.
  * C0's "to 2 dp" = |R_AGREE - 0.648| <= 0.005; the 4-dp value is printed and becomes the number of record.
  * Verdict-rule precedence: if F1 fires the sentence of record is the "unexplained judge order" one (C1 is then FAILED on
    its matched-R half whatever beta reads); otherwise C1 HELD -> the verbosity sentence; otherwise UNDETERMINED on the
    mechanism with both numbers (this covers "half-held" and the both-fail-without-F1 case, which the rule does not name).
  * --selftest opens nothing of record; --dry-run reads the caches and the eval DB mode=ro and prints counts only;
    --run refuses if any outcome file exists (write-once).
"""
import os, sys, math, random, csv, time, argparse, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import profile_r_filtered as prf
import profile_reliability as pr
import bias_audit as ba

OUT_DIR = os.path.join(ROOT, "experiment_results", "x12_crossdomain")
OUT = os.path.join(OUT_DIR, "agree_order_outcome.txt")
OUT_CELLS = os.path.join(OUT_DIR, "agree_order_cells.csv")
OUT_MODELS = os.path.join(OUT_DIR, "agree_order_models.csv")
SCRATCH = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "claude", "Z--FAC-TUBerlin-THESIS-TaxoArena",
                       "7c10e5cb-d16b-4a0e-864a-f3a6151d835b", "scratchpad", "agree_order")
POOL = prf.POOL
EXCLUDE = prf.EXCLUDE
SEED = 7                      # the halving seed of record (PROFILE-RELIABILITY / PROFILE-R-FILTERED)
BOOT_SEED = 2026
BOOT_B = 1000
MATCH_CUT = 300               # H3b's cut, chars
SUPPORT = 120
Z = 1.96
RECORDED_AGREE_R = 0.648      # the reviewer's scratch reading (docs/reviews/2026-09-18_night_batch.md)
RECORDED_COUNTS = dict(agree12=3076, agree20=5846, dis12=5276, dis20=5166, und12=790, und20=1382)
RECORDED_RANDOM_BAND = (0.46, 0.50)
H3_BETA = 0.39                # H3's +0.39 / 1k on all decisive matches (the comparator)
TD_BOTH_RIGHT = dict(easy=3.44, mid=2.69, hard=1.32)   # TOPIC-DIFFICULTY L5145-5146 both-right composition
# PROFILE-DEVIATION-CERT's 22 certified cells (L5784-5793): (model, anchor, delta', wrong_sign, established)
CERTIFIED = [
    ("Llama-2-7b-hf", "Physics", -0.480, False, False), ("Meta-Llama-3_1-70B-Instruct", "Law", -0.476, False, False),
    ("Qwen1.5-110B", "Math", +0.446, True, False), ("Yi-6b-Chat", "Chemistry", -0.640, False, False),
    ("Yi-6b-Chat", "Physics", -0.380, False, False), ("arx_0314", "Physics", +0.494, False, False),
    ("arx_3", "History", +0.527, False, False), ("arx_3", "Math", -0.385, True, True),
    ("claude-3-5-haiku-20241022", "Math", -0.635, True, False), ("claude-3-5-haiku-20241022", "Psychology", +0.539, False, False),
    ("claude-3-5-sonnet-20241022", "Law", +0.590, True, True), ("claude-3-5-sonnet-20241022", "Math", -0.537, True, False),
    ("deepseek-chat-v2_5", "Law", -0.469, False, False), ("deepseek-chat-v2_5", "Math", +0.478, False, False),
    ("deepseek-chat-v2_5", "Philosophy", -0.622, False, False), ("deepseek-chat-v2_5", "Psychology", -0.396, True, False),
    ("gemini-3.1-pro_5-shots", "Law", +0.686, True, True), ("gemini-3.1-pro_5-shots", "Other", -0.767, False, False),
    ("gemini-3.1-pro_5-shots", "Physics", +0.473, False, False), ("gemini-3.1-pro_5-shots", "Psychology", -0.441, False, False),
    ("gpt-4o-2024-08-06", "History", +0.520, True, False), ("iask_pro", "Biology", +0.552, False, False),
]
WRONG_SIGN = [c for c in CERTIFIED if c[3]]
assert len(WRONG_SIGN) == 8 and sum(1 for c in WRONG_SIGN if c[4]) == 3
sb = pr.sb


# ----------------------------------------------------------------------------------------------- small numerics
def spearman(xs, ys):
    import rejudge_grok as rj
    return rj.spearman(xs, ys)   # the record's tie-aware ranks


def mean(v):
    return sum(v) / len(v) if v else float("nan")


def pct(v, p):
    s = sorted(v); n = len(s)
    if not n: return float("nan")
    k = p * (n - 1); lo = int(math.floor(k)); hi = min(lo + 1, n - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def inv3(H):
    """Gauss-Jordan inverse of a 3 x 3 with partial pivoting."""
    n = 3; A = [H[i][:] + [1.0 if j == i else 0.0 for j in range(n)] for i in range(n)]
    for i in range(n):
        piv = max(range(i, n), key=lambda r: abs(A[r][i])); A[i], A[piv] = A[piv], A[i]
        p = A[i][i]
        A[i] = [x / p for x in A[i]]
        for r in range(n):
            if r != i and A[r][i] != 0.0:
                f = A[r][i]; A[r] = [x - f * y for x, y in zip(A[r], A[i])]
    return [row[n:] for row in A]


def cluster_se(X, Y, C, b):
    """Question-clustered sandwich SE for bias_audit._logit3's three coefficients at b; X = [(x1, x2)], C = cluster ids."""
    H = [[1e-9 if i == j else 0.0 for j in range(3)] for i in range(3)]
    G = defaultdict(lambda: [0.0, 0.0, 0.0])
    for (x1, x2), y, c in zip(X, Y, C):
        z = max(-30, min(30, b[0] + b[1] * x1 + b[2] * x2)); p = 1 / (1 + math.exp(-z))
        xs = (1.0, x1, x2)
        for i in range(3):
            G[c][i] += (y - p) * xs[i]
            for j in range(3): H[i][j] += p * (1 - p) * xs[i] * xs[j]
    M = [[0.0] * 3 for _ in range(3)]
    for g in G.values():
        for i in range(3):
            for j in range(3): M[i][j] += g[i] * g[j]
    Hi = inv3(H)
    V = [[sum(Hi[i][k] * M[k][l] * Hi[l][j] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
    return [math.sqrt(max(0.0, V[i][i])) for i in range(3)], len(G)


def fit_len(rows, L, x2_of):
    """H3's logistic on decisive rows: verdict-for-A ~ dlen/1k + x2. rows = (a, b, q, w, ...); x2_of(q, a, b) -> float.
    Returns dict(beta, se_model, se_cluster, z, lo, hi, n, nq, beta2, se2_cluster)."""
    X, Y, C = [], [], []
    for r in rows:
        a, b, q, w = r[0], r[1], r[2], r[3]
        if w not in (a, b): continue
        la, lb = L.get((q, a)), L.get((q, b))
        if la is None or lb is None: continue
        X.append(((la - lb) / 1000.0, float(x2_of(q, a, b)))); Y.append(1.0 if w == a else 0.0); C.append(q)
    if len(Y) < 30:
        return dict(beta=float("nan"), se_model=float("nan"), se_cluster=float("nan"), z=float("nan"), lo=float("nan"), hi=float("nan"), n=len(Y), nq=len(set(C)), beta2=float("nan"), se2_cluster=float("nan"))
    b, s = ba._logit3(X, Y)
    sc, nq = cluster_se(X, Y, C, b)
    return dict(beta=b[1], se_model=s[1], se_cluster=sc[1], z=b[1] / sc[1] if sc[1] > 0 else float("nan"),
                lo=b[1] - Z * sc[1], hi=b[1] + Z * sc[1], n=len(Y), nq=nq, beta2=b[2], se2_cluster=sc[2])


# ----------------------------------------------------------------------------------------------- boards
def board_R(rows, usable, qsel, models, rng_seed=SEED, demean=None):
    """The instrument the 0.648 was read with: cells = each anchor's judged questions with >= 1 verdict in `rows`;
    pr.reliability (40 halvings, Random(rng_seed), min_cell 25), model-demeaned unless `demean` is given; SB."""
    by = defaultdict(list)
    for r in rows: by[r[2]].append(r[:4])
    cells = {c: [q for q in v if q in by] for c, v in usable.items()}
    r, sd, n = pr.reliability(cells, qsel, prf.jb_for(by, models), models, random.Random(rng_seed), demean=demean or pr.demean_by_model)
    return dict(R=sb(r), r=r, sd=sd, n=n, q={c: len(v) for c, v in cells.items()}, matches={c: sum(len(by[q]) for q in v) for c, v in cells.items()})


def pooled_theta(rows, models):
    import judge_free_tests as jf
    return jf.board_from([(r[0], r[1], 0.5 if r[3] == "TIE" else (1.0 if r[3] == r[0] else 0.0), 1.0) for r in rows], models)


def anchor_mean_theta(rows, anc_of, usable, models):
    import judge_free_tests as jf
    byc = defaultdict(list)
    for r in rows: byc[anc_of[r[2]]].append(r)
    th = {c: jf.board_from([(r[0], r[1], 0.5 if r[3] == "TIE" else (1.0 if r[3] == r[0] else 0.0), 1.0) for r in v], models) for c, v in byc.items() if c in usable}
    return {m: mean([th[c][m] for c in th]) for m in models}, th


# ----------------------------------------------------------------------------------------------- (P) position
def pos_shares(rows):
    n = len(rows)
    if not n: return dict(n=0, first=float("nan"), second=float("nan"), union=float("nan"), decided=float("nan"), tie=float("nan"))
    f = sum(1 for r in rows if r[4] == "Model A" and r[5] == "Model A")
    s = sum(1 for r in rows if r[4] == "Model B" and r[5] == "Model B")
    d = sum(1 for r in rows if r[3] in (r[0], r[1]))
    t = sum(1 for r in rows if r[3] == "TIE")
    return dict(n=n, first=f / n, second=s / n, union=(f + s) / n, decided=d / n, tie=t / n, nf=f, ns=s, nd=d, nt=t)


def pos_diff_boot(agree, disagree, B=BOOT_B, seed=BOOT_SEED):
    """AGREE - DISAGREE differences of the position shares; question-clustered bootstrap over the union of questions."""
    byq_a = defaultdict(list); byq_d = defaultdict(list)
    for r in agree: byq_a[r[2]].append(r)
    for r in disagree: byq_d[r[2]].append(r)
    qs = sorted(set(byq_a) | set(byq_d)); rng = random.Random(seed)
    keys = ("first", "second", "union", "decided", "tie")
    stat = lambda A, D: {k: pos_shares(A)[k] - pos_shares(D)[k] for k in keys}
    point = stat(agree, disagree)
    draws = defaultdict(list)
    for _ in range(B):
        draw = [qs[rng.randrange(len(qs))] for _ in qs]
        A = [r for q in draw for r in byq_a.get(q, ())]; D = [r for q in draw for r in byq_d.get(q, ())]
        st = stat(A, D)
        for k in keys: draws[k].append(st[k])
    return {k: (point[k], pct(draws[k], 0.025), pct(draws[k], 0.975)) for k in keys}, len(qs)


# ----------------------------------------------------------------------------------------------- (D) deviation cells
def cell_longer(rows_anchor, m, L, K, B=BOOT_B, seed=BOOT_SEED):
    """rows_anchor: the anchor's merged rows. Among m's decisive wins, the share where m is strictly longer; the anchor's
    both-right decisive matches' share where the winner is strictly longer; question-clustered bootstrap on the difference."""
    byq = defaultdict(list)
    for r in rows_anchor: byq[r[2]].append(r)
    qs = sorted(byq)

    def stats(qlist):
        w_long = w_n = w_eq = 0; b_long = b_n = b_eq = 0; wq = set()
        for q in qlist:
            for r in byq[q]:
                a, b, _, w = r[0], r[1], r[2], r[3]
                if w not in (a, b): continue
                lw, ll = L.get((q, w)), L.get((q, b if w == a else a))
                if lw is None or ll is None: continue
                if w == m:
                    w_n += 1; w_long += lw > ll; w_eq += lw == ll; wq.add(q)
                if K[q].get(a) == 1 and K[q].get(b) == 1:
                    b_n += 1; b_long += lw > ll; b_eq += lw == ll
        return (w_long / w_n if w_n else float("nan"), w_n, w_eq, len(wq), b_long / b_n if b_n else float("nan"), b_n, b_eq)

    pt = stats(qs); rng = random.Random(seed); diffs = []
    for _ in range(B):
        draw = [qs[rng.randrange(len(qs))] for _ in qs]
        s = stats(draw)
        if s[0] == s[0] and s[4] == s[4]: diffs.append(s[0] - s[4])
    d = pt[0] - pt[4] if pt[0] == pt[0] and pt[4] == pt[4] else float("nan")
    lo, hi = (pct(diffs, 0.025), pct(diffs, 0.975)) if len(diffs) > 50 else (float("nan"), float("nan"))
    return dict(win_share=pt[0], wins=pt[1], win_eq=pt[2], win_q=pt[3], base_share=pt[4], base_n=pt[5], base_eq=pt[6], diff=d, lo=lo, hi=hi, n_boot=len(diffs))


# ----------------------------------------------------------------------------------------------- data of record
def load(say):
    """prf.load_record (the pins, the filter, K / P for the 20 models, the anchors) + the two single-order votes per
    match, the lengths, and the full keyed roster for the difficulty terciles."""
    import rejudge_grok as rj, stack_judge as sj, x20_replications as xr
    D = prf.load_record(say)
    D["by_m"] = defaultdict(list)
    for r in D["rows_m"]: D["by_m"][r[2]].append(r)
    prf.filter_report(D, say)
    # the single-order votes (vote1 in order 1; vote2_raw in order 2, where model_b is presented first)
    full = {}
    for name, path, ref in (("x12", sj.cache_path(), D["r12"]), ("x20", xr.X20, D["r20"])):
        con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
        rows = [(a, b, q, w, v1, v2, mid, anc) for mid, a, b, q, w, v1, v2, iv, anc in
                con.execute("SELECT match_id, model_a, model_b, qid, winner, vote1, vote2_raw, invalid, anchor FROM verdicts") if not iv]
        con.close()
        if sorted(r[:4] for r in rows) != sorted(ref):
            raise SystemExit("[PIN] the vote columns' rows do not match the loader's rows for %s" % name)
        bad = sum(1 for r in rows if r[4] not in ("Model A", "Model B", "TIE") or r[5] not in ("Model A", "Model B", "TIE"))
        if bad: raise SystemExit("[PIN] %d rows with an unexpected single-order vote in %s" % (bad, name))
        # consistency of the recorded dual-order verdict with the two votes (rj.combine_orders)
        name_of = lambda r, w: r[0] if w == "Model A" else (r[1] if w == "Model B" else w)
        mism = sum(1 for r in rows if name_of(r, rj.combine_orders(r[4], r[5])[0]) != r[3])
        if mism: raise SystemExit("[PIN] %d rows whose recorded winner is not combine_orders(vote1, vote2_raw) in %s" % (mism, name))
        full[name] = rows
    anc_of = {q: D["anc_of"](q) for q in D["qsel"]}
    disagree_anchor_col = sum(1 for name in full for r in full[name] if r[7] != anc_of.get(r[2]))
    say("  single-order votes loaded for x12 %d / x20 %d rows; every recorded winner = combine_orders(vote1, vote2_raw); cache anchor"
        % (len(full["x12"]), len(full["x20"])))
    say("  column vs the routing anchor of record: %d rows differ (the routing anchor is used)" % disagree_anchor_col)
    # lengths on the 20 models and the full keyed roster for the difficulty instrument
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB.replace("\\", "/"), uri=True)
    L = {}; Kall = defaultdict(dict); models20 = set(D["models20"]); qsel = D["qsel"]
    for q, m, out, c in ev.execute("SELECT question_id, model_name, model_output, is_correct FROM eval_results"):
        if q not in qsel or m == EXCLUDE: continue
        Kall[q][m] = int(c or 0)
        if m in models20: L[(q, m)] = len(out or "")
    ev.close()
    missing = [(m, sum(1 for q in qsel if (q, m) not in L)) for m in sorted(models20) if any((q, m) not in L for q in qsel)]
    say("  lengths: len(eval_results.model_output) on the %d judged questions x 20 models: %d cells%s" % (len(qsel), len(L),
        "; missing per model: " + ", ".join("%s %d" % x for x in missing) if missing else " (every model has a row on every judged question)"))
    roster = sorted({m for q in Kall for m in Kall[q]})
    diff = {q: mean(list(Kall[q].values())) for q in qsel if Kall[q]}
    terc = {}
    for c, qs in D["usable"].items():
        order = sorted([q for q in qs if q in diff], key=lambda q: (diff[q], q)); n = len(order); b1, b2 = n // 3, (2 * n) // 3
        for i, q in enumerate(order): terc[q] = "easy" if i >= b2 else ("mid" if i >= b1 else "hard")
    say("  difficulty instrument (descriptive leg): %d-model keyed roster (%s excluded), rank terciles within each anchor, %d questions assigned" % (len(roster), EXCLUDE, len(terc)))
    D.update(full=full, anc_of=anc_of, L=L, terc=terc)
    return D


def partition(D):
    """AGREE / DISAGREE / UNDETERMINED per cache on the full rows (prf.verdict = the shipped rule); both-right / both-wrong."""
    P, K = D["P"], D["K"]
    out = {}
    for name in ("x12", "x20"):
        parts = defaultdict(list)
        for r in D["full"][name]:
            parts[prf.verdict(P.get(r[2], {}).get(r[0]), P.get(r[2], {}).get(r[1]))].append(r)
        out[name] = parts
    out["merged"] = {k: out["x12"][k] + out["x20"][k] for k in ("AGREE", "DISAGREE", "UNDETERMINED")}
    both_right = lambda r: K[r[2]].get(r[0]) == 1 and K[r[2]].get(r[1]) == 1
    for name in out:
        out[name]["AGREE_right"] = [r for r in out[name]["AGREE"] if both_right(r)]
        out[name]["AGREE_wrong"] = [r for r in out[name]["AGREE"] if not both_right(r)]
    return out


def matched(rows, L, cut=MATCH_CUT):
    return [r for r in rows if (r[2], r[0]) in L and (r[2], r[1]) in L and abs(L[(r[2], r[0])] - L[(r[2], r[1])]) <= cut]


# ----------------------------------------------------------------------------------------------- the run
def run(D, say, quick=False):
    t0 = time.time(); prog = lambda s: print("   ", s, "%.0fs" % (time.time() - t0), flush=True)
    models = D["models20"]; usable = D["usable"]; qsel = D["qsel"]; L = D["L"]; K = D["K"]; anc_of = D["anc_of"]
    S = partition(D)
    agree, dis = S["merged"]["AGREE"], S["merged"]["DISAGREE"]
    R = {}
    # ---- C0 gate
    say(""); say("=== C0 GATE: the six counts and the AGREE-only board R (40 halvings Random(7), model-demeaned, SB) ===")
    counts = dict(agree12=len(S["x12"]["AGREE"]), agree20=len(S["x20"]["AGREE"]), dis12=len(S["x12"]["DISAGREE"]), dis20=len(S["x20"]["DISAGREE"]),
                  und12=len(S["x12"]["UNDETERMINED"]), und20=len(S["x20"]["UNDETERMINED"]))
    gate_counts = counts == RECORDED_COUNTS
    say("  counts x12 AGREE / DISAGREE / UNDETERMINED %d / %d / %d, x20 %d / %d / %d vs recorded 3,076 / 5,276 / 790, 5,846 / 5,166 / 1,382: %s"
        % (counts["agree12"], counts["dis12"], counts["und12"], counts["agree20"], counts["dis20"], counts["und20"], "EXACT" if gate_counts else "MISMATCH"))
    bA = board_R(agree, usable, qsel, models); prog("AGREE-only board")
    gate_R = abs(bA["R"] - RECORDED_AGREE_R) <= 0.005
    say("  AGREE-only board R = %.4f (r %.4f, halving SD %.4f, %d halvings) vs the reviewer's 0.648: %s (|diff| %.4f <= 0.005)"
        % (bA["R"], bA["r"], bA["sd"], bA["n"], "REPRODUCED" if gate_R else "NOT REPRODUCED", abs(bA["R"] - RECORDED_AGREE_R)))
    say("  AGREE q_distinct per anchor: %s" % ", ".join("%s %d" % (c, bA["q"][c]) for c in usable))
    bA2 = board_R(agree, usable, qsel, models, demean=pr.demean_two_way); prog("AGREE-only interaction-only")
    say("  interaction-only (two-way demeaned) AGREE-only R beside: %.4f" % bA2["R"])
    R.update(counts=counts, gate_counts=gate_counts, gate_R=gate_R, R_agree=bA["R"], R_agree_two=bA2["R"], bA=bA)
    gate = gate_counts and gate_R
    if not gate:
        say("  GATE FAILED: nothing below is a number of record (printed for diagnosis only).")
    # the reviewer's random band beside (random matches of AGREE's size from the whole board, seeds 42..44)
    n_ag = defaultdict(int)
    for r in agree: n_ag[anc_of[r[2]]] += 1
    by_anchor_all = defaultdict(list)
    for r in D["full"]["x12"] + D["full"]["x20"]: by_anchor_all[anc_of[r[2]]].append(r)
    band = []
    for s in range(3 if not quick else 1):
        rng = random.Random(42 + s); sub = []
        for c in usable: sub += rng.sample(by_anchor_all[c], n_ag[c])
        band.append(board_R(sub, usable, qsel, models)["R"])
    prog("random band")
    say("  random matches of AGREE's size from the whole board (seeds 42..%d): R %s (the reviewer's band 0.46-0.50)" % (41 + len(band), ", ".join("%.4f" % x for x in band)))
    R["band"] = band
    # ---- (L1) H3's logistic
    say(""); say("=== (L1) H3's logistic on AGREE decisive matches: verdict-for-A ~ beta_len x (len_A - len_B)/1k + both-right indicator; question-clustered SE ===")
    say("  %-34s %6s %6s %9s %9s %9s %7s  %-20s %s" % ("population", "n_dec", "n_q", "beta_len", "SE_clust", "SE_model", "z", "95% CI (clustered)", "x2 (both-right / gtDiff coef)"))
    br = lambda q, a, b: 1.0 if (K[q].get(a) == 1 and K[q].get(b) == 1) else 0.0
    gt = lambda q, a, b: (K[q].get(a, 0) - K[q].get(b, 0))
    fits = {}
    for label, rows, x2 in (("AGREE decisive, merged", agree, br), ("AGREE decisive, x12", S["x12"]["AGREE"], br), ("AGREE decisive, x20", S["x20"]["AGREE"], br),
                            ("AGREE both-right, merged", S["merged"]["AGREE_right"], lambda q, a, b: 0.0), ("AGREE both-wrong, merged", S["merged"]["AGREE_wrong"], lambda q, a, b: 0.0),
                            ("DISAGREE decisive, merged (H3 spec)", dis, gt), ("DISAGREE decisive, x12 (H3 spec)", S["x12"]["DISAGREE"], gt), ("DISAGREE decisive, x20 (H3 spec)", S["x20"]["DISAGREE"], gt),
                            ("ALL decisive, merged (H3 spec)", D["full"]["x12"] + D["full"]["x20"], gt)):
        f = fit_len(rows, L, x2); fits[label] = f
        x2s = "" if "both-" in label else "%+.3f (SE %.3f)" % (f["beta2"], f["se2_cluster"])
        say("  %-34s %6d %6d %+9.4f %9.4f %9.4f %+7.2f  [%+.3f, %+.3f]     %s" % (label, f["n"], f["nq"], f["beta"], f["se_cluster"], f["se_model"], f["z"], f["lo"], f["hi"], x2s))
    say("  comparators: H3 +0.39 / 1k on all decisive matches (x12, Mistral cell arm); TOPIC-DIFFICULTY both-right composition +3.44 / +2.69 / +1.32 by tercile.")
    R["fits"] = fits
    # descriptive: by anchor and by tercile
    say("  beta_len on AGREE decisive by anchor (descriptive, x2 = both-right):")
    by_c = defaultdict(list)
    for r in agree: by_c[anc_of[r[2]]].append(r)
    R["by_anchor"] = {}
    for c in usable:
        f = fit_len(by_c[c], L, br); R["by_anchor"][c] = f
        say("    %-18s n_dec %5d q %4d beta %+7.3f [%+.3f, %+.3f]" % (c, f["n"], f["nq"], f["beta"], f["lo"], f["hi"]))
    say("  beta_len by TOPIC-DIFFICULTY tercile (descriptive; both-right rows are the composition line's population):")
    R["by_terc"] = {}
    for t in ("easy", "mid", "hard"):
        fa = fit_len([r for r in agree if D["terc"].get(r[2]) == t], L, br)
        fb = fit_len([r for r in S["merged"]["AGREE_right"] if D["terc"].get(r[2]) == t], L, lambda q, a, b: 0.0)
        fall = fit_len([r for r in D["full"]["x12"] + D["full"]["x20"] if D["terc"].get(r[2]) == t and br(r[2], r[0], r[1])], L, lambda q, a, b: 0.0)
        R["by_terc"][t] = (fa, fb, fall)
        say("    %-5s AGREE decisive %+6.3f [%+.3f, %+.3f] (n %d) | AGREE both-right %+6.3f [%+.3f, %+.3f] (n %d) | ALL both-right decisive %+6.3f [%+.3f, %+.3f] (n %d; TOPIC-DIFFICULTY %+.2f)"
            % (t, fa["beta"], fa["lo"], fa["hi"], fa["n"], fb["beta"], fb["lo"], fb["hi"], fb["n"], fall["beta"], fall["lo"], fall["hi"], fall["n"], TD_BOTH_RIGHT[t]))
    prog("logistics")
    # ---- thetas: AGREE pooled, AGREE anchor-mean, unfiltered pooled, matched pooled; lengths; key
    m_agree = matched(agree, L)
    th_agree = pooled_theta(agree, models); th_agree_am, th_agree_anchor = anchor_mean_theta(agree, anc_of, usable, models)
    th_unf = pooled_theta(D["full"]["x12"] + D["full"]["x20"], models); th_unf_am, _ = anchor_mean_theta(D["full"]["x12"] + D["full"]["x20"], anc_of, usable, models)
    th_mat = pooled_theta(m_agree, models); th_mat_am, _ = anchor_mean_theta(m_agree, anc_of, usable, models)
    mlen = {m: mean([L[(q, m)] for q in qsel if (q, m) in L]) for m in models}
    kacc = {m: mean([K[q][m] for q in qsel if m in K.get(q, {})]) for m in models}
    n_ag_m = defaultdict(int)
    for r in agree: n_ag_m[r[0]] += 1; n_ag_m[r[1]] += 1
    R.update(th_agree=th_agree, th_agree_am=th_agree_am, th_unf=th_unf, th_mat=th_mat, th_mat_am=th_mat_am, mlen=mlen, kacc=kacc, n_ag_m=n_ag_m, th_unf_am=th_unf_am)
    v = lambda d: [d[m] for m in models]
    rho = dict(len=spearman(v(th_agree), v(mlen)), len_am=spearman(v(th_agree_am), v(mlen)), unf=spearman(v(th_agree), v(th_unf)), unf_am=spearman(v(th_agree_am), v(th_unf_am)),
               key=spearman(v(th_agree), v(kacc)), key_am=spearman(v(th_agree_am), v(kacc)), mat_len=spearman(v(th_mat), v(mlen)), mat_len_am=spearman(v(th_mat_am), v(mlen)),
               unf_len=spearman(v(th_unf), v(mlen)), unf_key=spearman(v(th_unf), v(kacc)), key_len=spearman(v(kacc), v(mlen)))
    R["rho"] = rho
    say(""); say("=== (L2) / (I) theta_AGREE over the 20 models (pooled BT fit on all AGREE matches; mean of the 14 per-anchor thetas beside) ===")
    say("  PLACEBO-ENTRY's caveat: the theta SCALE under an answer-agreement selection is not the board's (the filter widened it +13%); only Spearman is read; no position is published.")
    say("  %-30s %9s %9s %9s %9s %9s %9s %7s" % ("model", "th_AGREE", "th_AGR_am", "th_match", "th_unfilt", "mean_len", "key_acc", "n_AGR"))
    for m in sorted(models, key=lambda m: -th_agree[m]):
        say("  %-30s %+9.3f %+9.3f %+9.3f %+9.3f %9.0f %9.4f %7d" % (m, th_agree[m], th_agree_am[m], th_mat[m], th_unf[m], mlen[m], kacc[m], n_ag_m[m]))
    say("  Spearman(theta_AGREE, mean length)      = %+.4f  (anchor-mean pooling %+.4f)   [P2 bar >= 0.6]" % (rho["len"], rho["len_am"]))
    say("  Spearman(theta_AGREE, unfiltered theta) = %+.4f  (anchor-mean pooling %+.4f)" % (rho["unf"], rho["unf_am"]))
    say("  Spearman(theta_AGREE, key accuracy)     = %+.4f  (anchor-mean pooling %+.4f)   [P7 band [-0.35, 0.05]]" % (rho["key"], rho["key_am"]))
    say("  Spearman(theta_matched, mean length)    = %+.4f  (anchor-mean pooling %+.4f)   (if length is the mechanism the matched order loses it)" % (rho["mat_len"], rho["mat_len_am"]))
    say("  beside: Spearman(unfiltered theta, mean length) %+.4f; (unfiltered theta, key) %+.4f; (key, mean length) %+.4f" % (rho["unf_len"], rho["unf_key"], rho["key_len"]))
    import rejudge_grok as rj
    top4_agree = sorted(sorted(models, key=lambda m: -th_agree[m])[:4]); top4_key = sorted(sorted(models, key=lambda m: -kacc[m])[:4]); top_cluster = sorted(rj.TOP_CLUSTER)
    R.update(top4_agree=top4_agree, top4_key=top4_key, top_cluster=top_cluster)
    say("  AGREE-only top-4 as a SET (no rank): {%s}" % ", ".join(top4_agree))
    say("  key's top cluster (rj.TOP_CLUSTER):   {%s}; key top-4 by accuracy on the judged questions: {%s}; overlap with the AGREE set %d / %d"
        % (", ".join(top_cluster), ", ".join(top4_key), len(set(top4_agree) & set(top_cluster)), len(set(top4_agree) & set(top4_key))))
    # ---- (L3) length-matched AGREE-only R
    say(""); say("=== (L3) length-MATCHED AGREE-only split-half R (|len_A - len_B| <= %d chars; same instrument) ===" % MATCH_CUT)
    bM = board_R(m_agree, usable, qsel, models); prog("matched board")
    bM2 = board_R(m_agree, usable, qsel, models, demean=pr.demean_two_way); prog("matched interaction-only")
    low = [c for c in usable if bM["q"][c] < SUPPORT]
    say("  matched AGREE matches: %d of %d (%.1f%%); per anchor (matches / q_distinct): %s" % (len(m_agree), len(agree), 100 * len(m_agree) / len(agree),
        ", ".join("%s %d / %d%s" % (c, bM["matches"][c], bM["q"][c], "*" if bM["q"][c] < SUPPORT else "") for c in usable)))
    say("  matched AGREE-only R = %.4f (r %.4f, halving SD %.4f, %d halvings); interaction-only %.4f; support: %s"
        % (bM["R"], bM["r"], bM["sd"], bM["n"], bM2["R"], ("UNDETERMINED-by-support (%s below %d q; the R is still read with the count)" % (", ".join("%s %d" % (c, bM["q"][c]) for c in low), SUPPORT)) if low else "every anchor >= %d q" % SUPPORT))
    n_m = defaultdict(int)
    for r in m_agree: n_m[anc_of[r[2]]] += 1
    by_c_ag = defaultdict(list)
    for r in agree: by_c_ag[anc_of[r[2]]].append(r)
    comp = []
    for s in range(5 if not quick else 2):
        rng = random.Random(42 + s); sub = []
        for c in usable: sub += rng.sample(by_c_ag[c], n_m[c])
        comp.append(board_R(sub, usable, qsel, models)["R"])
    prog("random same-size AGREE comparator")
    say("  random same-size subsample of AGREE (per anchor the matched count; seeds 42..%d): R %s, mean %.4f" % (41 + len(comp), ", ".join("%.4f" % x for x in comp), mean(comp)))
    drop = R["R_agree"] - bM["R"]; supp = R["R_agree"] - mean(comp)
    say("  decomposition (PROFILE-R-FILTERED's reading applied to this cut): AGREE 0.648 -> matched %.4f = %+.4f; support (random same size) accounts for %+.4f (%s), selection %+.4f"
        % (bM["R"], -drop, -supp, ("%.0f%%" % (100 * supp / drop)) if drop > 0 else "n/a", -(drop - supp)))
    R.update(bM=bM, bM2=bM2, comp=comp, low=low, n_matched=len(m_agree))
    # ---- (P) position
    say(""); say("=== (P) POSITION on AGREE vs DISAGREE matches (the two single-order votes behind the dual-order verdict; no protocol change) ===")
    say("  %-8s %-9s %6s %8s %8s %8s %8s %8s" % ("cache", "set", "n", "1st-pos", "2nd-pos", "union", "decided", "tie"))
    P_res = {}
    for name in ("x12", "x20", "merged"):
        for st in ("AGREE", "DISAGREE"):
            sh = pos_shares(S[name][st]); P_res[(name, st)] = sh
            say("  %-8s %-9s %6d %8.4f %8.4f %8.4f %8.4f %8.4f" % (name, st, sh["n"], sh["first"], sh["second"], sh["union"], sh["decided"], sh["tie"]))
        sh = pos_shares(S[name]["UNDETERMINED"])
        say("  %-8s %-9s %6d %8.4f %8.4f %8.4f %8.4f %8.4f   (beside; not AGREE)" % (name, "UNDET.", sh["n"], sh["first"], sh["second"], sh["union"], sh["decided"], sh["tie"]))
    dif, nq = pos_diff_boot(agree, dis, B=BOOT_B if not quick else 200); prog("position bootstrap")
    R["pos"] = dif; R["pos_shares"] = P_res
    say("  AGREE - DISAGREE (merged), question-clustered bootstrap over %d questions (B = %d):" % (nq, BOOT_B if not quick else 200))
    for k, lab in (("first", "both favour FIRST position (the registered position-consistent share; C2 / P6)"), ("second", "both favour SECOND position"),
                   ("union", "either (union)"), ("decided", "decided consistently for one contestant"), ("tie", "tie rate (P5 bar >= +10pp)")):
        p, lo, hi = dif[k]
        say("    %-72s %+8.4f [%+.4f, %+.4f]" % (lab, p, lo, hi))
    # ---- (D) deviation-residue leg
    say(""); say("=== (D) DEVIATION-RESIDUE LEG (registered expecting UNDETERMINED): the 8 wrong-sign PROFILE-DEVIATION-CERT cells ===")
    say("  among m's in-anchor decisive WINS (merged board): share where m's answer is strictly longer; baseline = the anchor's both-right decisive matches' longer-answer-wins share;")
    say("  question-clustered bootstrap CI on the difference (B = %d); UNDETERMINED below %d distinct questions behind the wins or with a CI including 0" % (BOOT_B if not quick else 200, SUPPORT))
    say("  %-28s %-12s %7s %5s %5s %5s %8s %6s %8s %8s %-18s %s" % ("model", "anchor", "delta'", "wins", "w_eq", "q_w", "longer%", "base_n", "base%", "diff", "95% CI", "status"))
    rows_anchor = defaultdict(list)
    for r in D["full"]["x12"] + D["full"]["x20"]: rows_anchor[anc_of[r[2]]].append(r)
    cells = []
    for m, a, dl, ws, est in CERTIFIED:
        if m not in models: raise SystemExit("[CELLS] %s is not on the merged roster" % m)
        c = cell_longer(rows_anchor[a], m, L, K, B=BOOT_B if not quick else 200)
        c.update(model=m, anchor=a, delta=dl, wrong_sign=ws, established=est)
        c["decidable"] = c["win_q"] >= SUPPORT and c["lo"] == c["lo"] and not (c["lo"] <= 0 <= c["hi"])
        c["status"] = ("DECIDABLE (%s)" % ("longer wins more" if c["diff"] > 0 else "longer wins less")) if c["decidable"] else "UNDETERMINED" + ("" if c["win_q"] >= SUPPORT else " (q_w < %d)" % SUPPORT)
        cells.append(c)
    for c in cells:
        if not c["wrong_sign"]: continue
        say("  %-28s %-12s %+7.3f %5d %5d %5d %8.3f %6d %8.3f %+8.3f [%+.3f, %+.3f] %-18s %s" % (c["model"], c["anchor"], c["delta"], c["wins"], c["win_eq"], c["win_q"], c["win_share"], c["base_n"], c["base_share"], c["diff"], c["lo"], c["hi"], c["status"], "wrong(established)" if c["established"] else "wrong sign"))
    say("  the other 14 certified cells beside (description only; no claim about any model's standing):")
    for c in cells:
        if c["wrong_sign"]: continue
        say("  %-28s %-12s %+7.3f %5d %5d %5d %8.3f %6d %8.3f %+8.3f [%+.3f, %+.3f] %-18s %s" % (c["model"], c["anchor"], c["delta"], c["wins"], c["win_eq"], c["win_q"], c["win_share"], c["base_n"], c["base_share"], c["diff"], c["lo"], c["hi"], c["status"], "right sign" if c["model"] != "iask_pro" else "FAIL anchor, PREDICTIVE-ONLY"))
    R["cells"] = cells; prog("deviation cells")
    R["gate"] = gate
    return R


def score(R, say):
    fits = R["fits"]; f = fits["AGREE decisive, merged"]; bM = R["bM"]; rho = R["rho"]; dif = R["pos"]
    say(""); say("=== CRITERIA, PREDICTIONS, FALSIFIER (scored as registered; L8135-8172) ===")
    c0 = R["gate"]
    say("  C0 GATE: AGREE-only R %.4f vs 0.648 to 2 dp %s; six counts %s -> %s" % (R["R_agree"], "REPRODUCED" if R["gate_R"] else "NOT REPRODUCED", "EXACT" if R["gate_counts"] else "MISMATCH", "HELD" if c0 else "FAILED"))
    beta_ok = f["beta"] >= 2.5 and f["lo"] > 0
    match_ok = bM["R"] < 0.50
    c1 = beta_ok and match_ok
    say("  C1 LENGTH IS THE MECHANISM: (L1) beta_len AGREE decisive merged %+.4f [%+.4f, %+.4f] >= +2.5 with CI excluding 0: %s; (L3) matched R %.4f < 0.50: %s -> %s"
        % (f["beta"], f["lo"], f["hi"], "yes" if beta_ok else "no", bM["R"], "yes" if match_ok else "no", "HELD" if c1 else ("FAILED (both halves)" if not beta_ok and not match_ok else "half-held")))
    p, lo, hi = dif["first"]
    c2 = abs(p) < 0.02 or (lo <= 0 <= hi)
    pu, lou, hiu = dif["union"]
    c2u = abs(pu) < 0.02 or (lou <= 0 <= hiu)
    say("  C2 POSITION IS NOT: AGREE - DISAGREE first-position-consistent share %+.4f [%+.4f, %+.4f]: %s (point < 2pp: %s; CI includes 0: %s); union reading %+.4f [%+.4f, %+.4f]: %s"
        % (p, lo, hi, "HELD" if c2 else "FAILED", "yes" if abs(p) < 0.02 else "no", "yes" if lo <= 0 <= hi else "no", pu, lou, hiu, "HELD" if c2u else "FAILED"))
    trio = dict(length=rho["len"], unfiltered_theta=rho["unf"], key=rho["key"])
    nearest = max(trio, key=lambda k: abs(trio[k]))
    say("  C3 IDENTITY (REPORTED): Spearman(theta_AGREE, length) %+.4f, (theta_AGREE, unfiltered theta) %+.4f, (theta_AGREE, key) %+.4f; largest |rho| = %s (%+.4f): the order's nearest description"
        % (rho["len"], rho["unf"], rho["key"], nearest, trio[nearest]))
    # predictions
    p1 = f["beta"] >= 2.5
    p2 = rho["len"] >= 0.6; p2_am = rho["len_am"] >= 0.6
    p3 = bM["R"] < 0.50
    fbr, fbw = fits["AGREE both-right, merged"], fits["AGREE both-wrong, merged"]
    p4 = abs(fbw["beta"] - fbr["beta"]) <= 1.0
    pt, lot, hit = dif["tie"]; p5 = pt >= 0.10
    p6 = abs(p) < 0.02
    p7 = -0.35 <= rho["key"] <= 0.05; p7_am = -0.35 <= rho["key_am"] <= 0.05
    ws = [c for c in R["cells"] if c["wrong_sign"]]; est = [c for c in ws if c["established"]]
    n_dec = sum(1 for c in ws if c["decidable"]); n_est_pos = sum(1 for c in est if c["diff"] == c["diff"] and c["diff"] > 0)
    p8 = n_dec == 0 and n_est_pos >= 2
    f1 = bM["R"] >= 0.60
    say("  P1 (plan) beta_len AGREE decisive >= +2.5 / 1k: %s (%+.4f)" % ("HELD" if p1 else "FAILED", f["beta"]))
    say("  P2 (plan) Spearman(theta_AGREE, mean length) >= 0.6: %s (%+.4f; anchor-mean pooling %+.4f -> %s)" % ("HELD" if p2 else "FAILED", rho["len"], rho["len_am"], "HELD" if p2_am else "FAILED"))
    say("  P3 (plan) matched AGREE-only R < 0.50: %s (%.4f)" % ("HELD" if p3 else "FAILED", bM["R"]))
    say("  P4 (registrar) both-wrong beta within +-1.0 of both-right: %s (both-right %+.3f, both-wrong %+.3f, diff %+.3f)" % ("HELD" if p4 else "FAILED", fbr["beta"], fbw["beta"], fbw["beta"] - fbr["beta"]))
    say("  P5 (registrar) AGREE tie rate exceeds DISAGREE by >= 10pp: %s (%+.4f [%+.4f, %+.4f])" % ("HELD" if p5 else "FAILED", pt, lot, hit))
    say("  P6 (registrar) first-position-consistent share differs by < 2pp: %s (%+.4f)" % ("HELD" if p6 else "FAILED", p))
    say("  P7 (registrar) Spearman(theta_AGREE, key) in [-0.35, 0.05]: %s (%+.4f; anchor-mean pooling %+.4f -> %s)" % ("HELD" if p7 else "FAILED", rho["key"], rho["key_am"], "HELD" if p7_am else "FAILED"))
    say("  P8 (registrar) (D) 0 of 8 decidable AND >= 2 of the 3 established cells with a positive point difference: %s (decidable %d of 8; established positive %d of 3)" % ("HELD" if p8 else "FAILED", n_dec, n_est_pos))
    say("  FALSIFIER F1 matched AGREE-only R >= 0.60 at the point: %s (%.4f; matched support: %s)" % ("FIRES" if f1 else "silent", bM["R"], "UNDETERMINED-by-support on " + ", ".join(R["low"]) if R["low"] else "every anchor >= %d q" % SUPPORT))
    say("  (D) leg: %s" % ("UNDETERMINED as registered (no cell clears both the %d-question rule and a CI excluding 0)" % SUPPORT if n_dec == 0 else "%d cell(s) decidable: %s" % (n_dec, "; ".join("%s / %s %+.3f [%+.3f, %+.3f]" % (c["model"], c["anchor"], c["diff"], c["lo"], c["hi"]) for c in ws if c["decidable"]))))
    say("  leakage / closed lines: no verdict re-drawn; no length control enters the recipe (H7 closed); the AGREE top-4 is a set; ARXIASK's frontier pair (DISAGREE by construction) is not re-read.")
    say(""); say("=== VERDICT (the registered rule, L8145-8149; precedence stated in the docstring) ===")
    if not c0:
        verdict = "GATE FAILED: no sentence of record."
    elif f1:
        verdict = ("C1 FAILED with the falsifier fired: the removed order is not length; an unexplained judge order on same-answer matches is a finding "
                   "(matched AGREE-only R %.4f >= 0.60 after length matching; beta_len %+.3f); the (P) / (I) legs are its only description: position difference %+.4f [%+.4f, %+.4f], "
                   "Spearman with unfiltered theta %+.3f, with key %+.3f, with length %+.3f." % (bM["R"], f["beta"], p, lo, hi, rho["unf"], rho["key"], rho["len"]))
    elif c1:
        verdict = ("C1 HELD: the selection term of PROFILE-R-FILTERED is verbosity: the same-answer matches carry the length order (beta_len %+.3f / 1k [%+.3f, %+.3f] on %d AGREE decisive matches; "
                   "length-matched AGREE-only R %.4f against 0.648 unmatched and %.3f for a random same-size subsample)." % (f["beta"], f["lo"], f["hi"], f["n"], bM["R"], mean(R["comp"])))
    else:
        verdict = ("UNDETERMINED on the mechanism (C1 %s): beta_len %+.3f [%+.3f, %+.3f] (bar +2.5, CI excluding 0: %s); length-matched AGREE-only R %.4f (bar < 0.50: %s; F1 >= 0.60 silent)."
                   % ("half-held" if beta_ok != match_ok else "FAILED on both halves without F1", f["beta"], f["lo"], f["hi"], "yes" if f["lo"] > 0 else "no", bM["R"], "yes" if match_ok else "no"))
    say("  " + verdict)
    say("  C0 %s | C1 %s | C2 %s | C3 REPORTED (%s) | P1 %s | P2 %s | P3 %s | P4 %s | P5 %s | P6 %s | P7 %s | P8 %s | F1 %s | (D) %s"
        % ("HELD" if c0 else "FAILED", "HELD" if c1 else ("half-held" if beta_ok != match_ok else "FAILED"), "HELD" if c2 else "FAILED", nearest,
           *["HELD" if x else "FAILED" for x in (p1, p2, p3, p4, p5, p6, p7, p8)], "FIRES" if f1 else "silent", "UNDETERMINED" if n_dec == 0 else "%d decidable" % n_dec))
    return dict(c0=c0, c1=c1, c2=c2, p=(p1, p2, p3, p4, p5, p6, p7, p8), f1=f1, verdict=verdict)


def write_csvs(D, R):
    models = D["models20"]
    with open(OUT_MODELS, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "theta_AGREE_pooled", "theta_AGREE_anchor_mean", "theta_matched_pooled", "theta_matched_anchor_mean", "theta_unfiltered_pooled", "mean_length_chars", "key_accuracy", "n_AGREE_matches"])
        for m in sorted(models, key=lambda m: -R["th_agree"][m]):
            w.writerow([m, "%.4f" % R["th_agree"][m], "%.4f" % R["th_agree_am"][m], "%.4f" % R["th_mat"][m], "%.4f" % R["th_mat_am"][m], "%.4f" % R["th_unf"][m], "%.1f" % R["mlen"][m], "%.4f" % R["kacc"][m], R["n_ag_m"][m]])
    with open(OUT_CELLS, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "anchor", "delta_prime", "established", "wins", "wins_equal_length", "q_behind_wins", "longer_share_in_wins", "baseline_n", "baseline_longer_share", "diff", "ci_lo", "ci_hi", "status"])
        for c in R["cells"]:
            if not c["wrong_sign"]: continue
            w.writerow([c["model"], c["anchor"], "%+.3f" % c["delta"], int(c["established"]), c["wins"], c["win_eq"], c["win_q"], "%.4f" % c["win_share"], c["base_n"], "%.4f" % c["base_share"], "%.4f" % c["diff"], "%.4f" % c["lo"], "%.4f" % c["hi"], c["status"]])


def write_once(path, txt):
    if os.path.exists(path): raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % path)
    open(path, "w", encoding="utf-8").write(txt + "\n")


# ----------------------------------------------------------------------------------------------- dry run
def dry_run(D, say):
    S = partition(D); L = D["L"]; anc_of = D["anc_of"]; usable = D["usable"]
    say(""); say("--- DRY RUN: the C0 count gate, the matched-set size per anchor, the 8 cells' match counts; no R, no beta ---")
    counts = dict(agree12=len(S["x12"]["AGREE"]), agree20=len(S["x20"]["AGREE"]), dis12=len(S["x12"]["DISAGREE"]), dis20=len(S["x20"]["DISAGREE"]), und12=len(S["x12"]["UNDETERMINED"]), und20=len(S["x20"]["UNDETERMINED"]))
    say("  AGREE x12 %d + x20 %d = %d (recorded 3,076 + 5,846 = 8,922); DISAGREE %d + %d = %d (5,276 + 5,166); UNDETERMINED %d + %d (790 + 1,382): %s"
        % (counts["agree12"], counts["agree20"], counts["agree12"] + counts["agree20"], counts["dis12"], counts["dis20"], counts["dis12"] + counts["dis20"], counts["und12"], counts["und20"], "EXACT" if counts == RECORDED_COUNTS else "MISMATCH"))
    ag = S["merged"]["AGREE"]; br = len(S["merged"]["AGREE_right"]); say("  AGREE both-right %d / both-wrong %d (a partition of AGREE by the key); decisive %d, ties %d" % (br, len(ag) - br, sum(1 for r in ag if r[3] != "TIE"), sum(1 for r in ag if r[3] == "TIE")))
    m = matched(ag, L)
    n_m = defaultdict(int); q_m = defaultdict(set); n_a = defaultdict(int); q_a = defaultdict(set)
    for r in ag: n_a[anc_of[r[2]]] += 1; q_a[anc_of[r[2]]].add(r[2])
    for r in m: n_m[anc_of[r[2]]] += 1; q_m[anc_of[r[2]]].add(r[2])
    say("  length-matched (|dlen| <= %d) AGREE matches %d of %d; per anchor AGREE matches / q -> matched matches / q (* = q < %d):" % (MATCH_CUT, len(m), len(ag), SUPPORT))
    for c in usable:
        say("    %-18s %5d / %4d -> %5d / %4d%s" % (c, n_a[c], len(q_a[c]), n_m[c], len(q_m[c]), " *" if len(q_m[c]) < SUPPORT else ""))
    say("  the 8 wrong-sign cells (model / anchor): in-anchor matches of m, decisive wins of m, distinct q behind the wins; anchor both-right decisive n:")
    rows_anchor = defaultdict(list)
    for r in D["full"]["x12"] + D["full"]["x20"]: rows_anchor[anc_of[r[2]]].append(r)
    K = D["K"]
    for mdl, a, dl, ws, est in WRONG_SIGN:
        ra = rows_anchor[a]; mine = [r for r in ra if mdl in (r[0], r[1])]; wins = [r for r in mine if r[3] == mdl]
        bdec = sum(1 for r in ra if r[3] != "TIE" and K[r[2]].get(r[0]) == 1 and K[r[2]].get(r[1]) == 1)
        say("    %-28s %-12s matches %4d, wins %4d, q_wins %4d%s, anchor both-right decisive %4d%s" % (mdl, a, len(mine), len(wins), len({r[2] for r in wins}), " (< %d)" % SUPPORT if len({r[2] for r in wins}) < SUPPORT else "", bdec, "  wrong(established)" if est else ""))
    say("  dry run: the gate R, the logistics, the thetas, the matched R, the position and deviation legs run under --run only; no outcome number printed.")


# ----------------------------------------------------------------------------------------------- selftest
def synthetic(kind, seed=3, n_models=20, n_anchors=8, q_per=150, mpq=6, p_pos=0.0, p_pos_base=0.05):
    """kind = 'length' (verdicts from length alone; per-(model, anchor) mean lengths so the length order is an interaction),
    'identity' (verdicts from a planted theta with anchor deviations; lengths per model only, independent of theta),
    'null' (coin-flip verdicts). p_pos_base plants first-position-consistent vote pairs on every match (recorded as TIE by
    the dual-order rule); p_pos plants them on AGREE matches in addition.
    Rows carry the record's shape (a, b, q, w, vote1, vote2_raw, match_id, anchor)."""
    import rejudge_grok as rj
    rng = random.Random(seed)
    models = ["m%02d" % i for i in range(n_models)]
    g = [rng.gauss(0, 1.0) for _ in models]; gl = [rng.gauss(0, 1.0) for _ in models]
    usable = {}; rows = []; L = {}; K = defaultdict(dict); P = defaultdict(dict); anc_of = {}
    qid = 0; mid = 0
    for j in range(n_anchors):
        c = "A%02d" % j; usable[c] = []
        theta = [x + rng.gauss(0, 1.0) for x in g]
        # length: per-(model, anchor) means (an interaction, so the length order survives model-demeaning), wide noise so the
        # |dlen| <= 300 band is a thin slice; identity / null: one mean for every model, tight noise (the band keeps ~60%)
        mu = [2000 + 700 * x + 700 * rng.gauss(0, 1.0) if kind == "length" else 2000.0 for x in gl]
        sd = 900 if kind == "length" else 250
        for _ in range(q_per):
            qid += 1; usable[c].append(qid); anc_of[qid] = c
            for i, m in enumerate(models):
                L[(qid, m)] = max(20, int(rng.gauss(mu[i], sd)))
                K[qid][m] = int(rng.random() < 0.5); P[qid][m] = "A" if rng.random() < 0.6 else "B"
            for _ in range(mpq):
                ia, ib = rng.sample(range(n_models), 2); a, b = models[ia], models[ib]; mid += 1
                if kind == "length": pa = 1 / (1 + math.exp(-3.0 * (L[(qid, a)] - L[(qid, b)]) / 1000.0))
                elif kind == "identity": pa = 1 / (1 + math.exp(-(theta[ia] - theta[ib])))
                else: pa = 0.5
                agree = P[qid][a] == P[qid][b]
                if rng.random() < p_pos_base + (p_pos if agree else 0.0):
                    v1, v2 = "Model A", "Model A"
                elif rng.random() < 0.15:
                    v1, v2 = "TIE", "TIE"
                else:
                    wa = rng.random() < pa; v1 = "Model A" if wa else "Model B"; v2 = "Model B" if wa else "Model A"
                w, flip, inv = rj.combine_orders(v1, v2)
                w = a if w == "Model A" else (b if w == "Model B" else w)     # the cache stores the model name
                rows.append((a, b, qid, w, v1, v2, mid, c))
    return dict(models20=models, usable=usable, qsel=set(anc_of), L=L, K=K, P=P, anc_of=anc_of, full=dict(x12=rows[: len(rows) // 2], x20=rows[len(rows) // 2:]))


def selftest():
    print("pool of record (NOT opened by --selftest): %s" % POOL)
    print("=== AGREE-ORDER --selftest (synthetic boards; nothing of record is opened) ===")
    t0 = time.time()
    res = {}
    for kind in ("length", "identity", "null"):
        D = synthetic(kind); S = partition(D); ag = S["merged"]["AGREE"]; models = D["models20"]; L = D["L"]; K = D["K"]
        br = lambda q, a, b: 1.0 if (K[q].get(a) == 1 and K[q].get(b) == 1) else 0.0
        f = fit_len(ag, L, br)
        mt = matched(ag, L)
        bU = board_R(ag, D["usable"], D["qsel"], models); bM = board_R(mt, D["usable"], D["qsel"], models)
        n_m = defaultdict(int); by_c = defaultdict(list)
        for r in mt: n_m[D["anc_of"][r[2]]] += 1
        for r in ag: by_c[D["anc_of"][r[2]]].append(r)
        rng = random.Random(42); sub = []
        for c in D["usable"]: sub += rng.sample(by_c[c], n_m[c])
        bS = board_R(sub, D["usable"], D["qsel"], models)
        th = pooled_theta(ag, models); mlen = {m: mean([L[(q, m)] for q in D["qsel"]]) for m in models}
        rho = spearman([th[m] for m in models], [mlen[m] for m in models])
        res[kind] = (f, bU, bM, rho, bS)
        print("  %-8s AGREE %5d (matched %5d): beta_len %+.3f [%+.3f, %+.3f] z %+.1f (SE clust %.3f / model %.3f) | R unmatched %.4f matched %.4f random-same-size %.4f | Spearman(theta, len) %+.3f  %.0fs"
              % (kind, len(ag), len(mt), f["beta"], f["lo"], f["hi"], f["z"], f["se_cluster"], f["se_model"], bU["R"], bM["R"], bS["R"], rho, time.time() - t0))
    f, bU, bM, rho, bS = res["length"]
    assert f["beta"] > 0 and f["lo"] > 0 and abs(f["beta"] - 3.0) < 1.0, "pure-length board: planted +3.0 / 1k not recovered"
    assert bU["R"] > 0.6, "pure-length board with per-anchor length deviations must read a reproducible unmatched R"
    assert bM["R"] < 0.35 and bS["R"] - bM["R"] > 0.2, "pure-length board: the length-matched R must fall towards 0 and below the same-size comparator (%.3f vs %.3f)" % (bM["R"], bS["R"])
    assert rho > 0.6, "pure-length board: theta must track mean length"
    f, bU, bM, rho, bS = res["identity"]
    assert abs(f["z"]) < 3, "pure-identity board: no length effect should be read"
    assert bU["R"] > 0.6 and bM["R"] > 0.5 and abs(bS["R"] - bM["R"]) < 0.15, "pure-identity board: matched R must stay near the same-size comparator (%.3f vs %.3f; unmatched %.3f)" % (bM["R"], bS["R"], bU["R"])
    f, bU, bM, rho, bS = res["null"]
    assert f["lo"] <= 0 <= f["hi"], "null board: the clustered CI must include 0"
    assert bU["R"] < 0.3, "null board: R must be near 0 (%.3f)" % bU["R"]
    # (L1) the x2 = 0 subset call of _logit3 must give the same beta_len as an independent two-parameter Newton fit
    D = synthetic("length"); S = partition(D)
    sub = S["merged"]["AGREE_right"]; f0 = fit_len(sub, D["L"], lambda q, a, b: 0.0)
    X = [((D["L"][(r[2], r[0])] - D["L"][(r[2], r[1])]) / 1000.0, 1.0 if r[3] == r[0] else 0.0) for r in sub if r[3] in (r[0], r[1])]
    b0 = b1 = 0.0
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in X:
            pp = 1 / (1 + math.exp(-max(-30, min(30, b0 + b1 * x)))); w = pp * (1 - pp)
            g0 += y - pp; g1 += (y - pp) * x; h00 += w; h01 += w * x; h11 += w * x * x
        det = h00 * h11 - h01 * h01; d0 = (h11 * g0 - h01 * g1) / det; d1 = (h00 * g1 - h01 * g0) / det
        b0 += d0; b1 += d1
        if max(abs(d0), abs(d1)) < 1e-12: break
    assert abs(f0["beta"] - b1) < 1e-6, "x2 = 0 call of _logit3 (%.8f) differs from the two-parameter fit (%.8f)" % (f0["beta"], b1)
    print("  x2 = 0 subset call of _logit3: beta_len %.6f = independent two-parameter Newton %.6f" % (f0["beta"], b1))
    # (P) planted first-position pairs on AGREE only
    Dp = synthetic("null", p_pos=0.15); Sp = partition(Dp)
    dif, nq = pos_diff_boot(Sp["merged"]["AGREE"], Sp["merged"]["DISAGREE"], B=200)
    p, lo, hi = dif["first"]
    print("  position: planted +0.15 first-position share on AGREE: AGREE - DISAGREE %+.4f [%+.4f, %+.4f] over %d questions" % (p, lo, hi, nq))
    assert 0.10 < p < 0.20 and lo > 0, "planted position effect not recovered"
    dif0, _ = pos_diff_boot(S["merged"]["AGREE"], S["merged"]["DISAGREE"], B=200)
    p0, lo0, hi0 = dif0["first"]
    print("  position: no planted effect: %+.4f [%+.4f, %+.4f]" % (p0, lo0, hi0))
    assert lo0 <= 0 <= hi0 and abs(p0) < 0.03 and hi0 - lo0 > 0.005, "position null did not close (or the CI is degenerate)"
    # (D) on the pure-length board every winner tends to be the longer answer; on the null board ~0.5
    rows_anchor = defaultdict(list)
    for r in D["full"]["x12"] + D["full"]["x20"]: rows_anchor[D["anc_of"][r[2]]].append(r)
    c = cell_longer(rows_anchor["A00"], "m00", D["L"], D["K"], B=200)
    Dn = synthetic("null"); rows_n = defaultdict(list)
    for r in Dn["full"]["x12"] + Dn["full"]["x20"]: rows_n[Dn["anc_of"][r[2]]].append(r)
    cn = cell_longer(rows_n["A00"], "m00", Dn["L"], Dn["K"], B=200)
    print("  deviation cell (length board) m00 / A00: wins %d (q %d) longer %.3f vs baseline %.3f, diff %+.3f [%+.3f, %+.3f]; null board: longer %.3f vs %.3f [%+.3f, %+.3f]"
          % (c["wins"], c["win_q"], c["win_share"], c["base_share"], c["diff"], c["lo"], c["hi"], cn["win_share"], cn["base_share"], cn["lo"], cn["hi"]))
    assert c["win_share"] > 0.8 and c["base_share"] > 0.8, "pure-length board: winners must be the longer answers"
    assert abs(cn["win_share"] - 0.5) < 0.15 and cn["lo"] <= 0 <= cn["hi"], "null board: the deviation cell must read ~0.5 with a CI including 0"
    # cluster SE sanity: with one row per cluster the sandwich must be finite and of the model SE's order
    X = [(random.Random(i).gauss(0, 1), 0.0) for i in range(400)]; Y = [1.0 if random.Random(i + 7).random() < 1 / (1 + math.exp(-x[0])) else 0.0 for i, x in enumerate(X)]
    b, s = ba._logit3(X, Y); sc, _ = cluster_se(X, Y, list(range(400)), b)
    assert 0.5 < sc[1] / s[1] < 2.0, "cluster SE with singleton clusters should be of the model SE's order"
    # write-once
    os.makedirs(SCRATCH, exist_ok=True); tmp = os.path.join(SCRATCH, "selftest_once.txt"); open(tmp, "w").write("x")
    try:
        write_once(tmp, "y"); raise AssertionError("write-once did not refuse")
    except SystemExit:
        pass
    os.remove(tmp)
    print("SELFTEST OK: pure-length board reads beta > 0 (planted +3.0 recovered), unmatched R high and matched R ~ 0, theta tracks length; pure-identity board reads")
    print("  matched R ~ unmatched R and no length effect; null board closes (CI includes 0, R ~ 0); planted first-position pairs recovered on AGREE only and the")
    print("  position null closes; deviation-cell shares and CIs behave; x2 = 0 subset call = two-parameter fit; cluster SE finite; write-once refuses.  %.0fs" % (time.time() - t0))


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--quick", action="store_true", help="fewer bootstrap draws and comparator seeds; NOT an outcome of record (refused with --run)")
    a = ap.parse_args()
    if sum(map(bool, (a.dry_run, a.selftest, a.run))) != 1: ap.error("exactly one of --dry-run, --selftest, --run")
    if a.selftest:
        selftest(); return
    if a.run and a.quick: raise SystemExit("--quick is not an outcome of record; use it with --dry-run only or not at all")
    import pool_guard
    Lns = []
    say = lambda s: (Lns.append(s), print(s, flush=True))
    say("pool of record: %s" % pool_guard.assert_pool_of_record(POOL))
    say("=== AGREE-ORDER: is the reproducible non-key order of the same-answer (AGREE) matches a LENGTH, a POSITION, or a contestant-identity order? ===")
    say("  registered 2026-09-19 (commit 5205c1d, L8065-L8222); zero calls; caches mode=ro; %s" % ("DRY RUN" if a.dry_run else "RUN"))
    say(""); say("--- DATA CHECK (the object, before any stratum is read; PROFILE-R-FILTERED's loader and filter) ---")
    D = load(say)
    if a.dry_run:
        dry_run(D, say); return
    for pth in (OUT, OUT_CELLS, OUT_MODELS):
        if os.path.exists(pth): raise SystemExit("[WRITE-ONCE] %s exists; not overwritten" % pth)
    R = run(D, say)
    V = score(R, say)
    say("  KEY DENOMINATOR restated: the 8,922 AGREE matches (x12 3,076 + x20 5,846) of the 2,811 judged questions of pool %s on the 14 bareq512_s42 anchors;" % POOL)
    say("  decisive AGREE = the non-TIE subset; the length-matched set as printed; DISAGREE = conv B's 10,442; both-right / both-wrong from eval_results.is_correct on the 20-model roster.")
    say("  McNEMAR-ESTABLISHED RULE: no wrong-direction count is read here; stated, not applied. Both tie conventions: ties are excluded from every logistic (decisive only,")
    say("  H3's rule) and counted as 0.5 in every BT fit (the board's rule); the tie rates themselves are printed in (P).")
    say("  files: %s, %s (8 rows), %s (20 rows); script tools/analysis/agree_order.py" % (OUT, OUT_CELLS, OUT_MODELS))
    txt = "\n".join(Lns)
    write_once(OUT, txt); write_csvs(D, R)
    print("written", OUT, OUT_CELLS, OUT_MODELS)


if __name__ == "__main__":
    main()
